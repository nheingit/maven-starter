import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from .database import get_db
import logging
import time

logger = logging.getLogger(__name__)

def scrape_hexdoc(url):
    logger.info(f"Starting to crawl: {url}")
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    library_path = parsed_url.path.split('/')[1]  # This will be 'reactor' in your case
    visited_urls = set()
    to_visit = [url]
    app_info = None
    max_links = 50  # Set the maximum number of links to scrape

    with get_db() as conn:
        cursor = conn.cursor()
        
        while to_visit and len(visited_urls) < max_links:
            current_url = to_visit.pop(0)
            if current_url in visited_urls:
                continue

            visited_urls.add(current_url)
            logger.info(f"Scraping: {current_url} ({len(visited_urls)}/{max_links})")

            try:
                response = requests.get(current_url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')

                if current_url == url:
                    # This is the main page
                    app_info = extract_app_info(soup, cursor)
                    logger.info(f"Extracted application info: {app_info}")
                
                if app_info and f'/{library_path}/' in current_url:
                    module_info = extract_module_info(soup, current_url, app_info['id'], cursor)
                    logger.info(f"Extracted module info: {module_info}")

                new_links = extract_hexdoc_links(soup, base_url, library_path)
                logger.info(f"Extracted {len(new_links)} new links to visit")
                to_visit.extend([link for link in new_links if link not in visited_urls])

                # Add a small delay to avoid overwhelming the server
                time.sleep(0.5)

            except requests.RequestException as e:
                logger.error(f"Error accessing the URL {current_url}: {e}")

            if len(visited_urls) >= max_links:
                logger.info(f"Reached the maximum number of links to scrape ({max_links})")
                break

        conn.commit()

    # Add these lines to check the database content after scraping
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM applications")
        app_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM modules")
        module_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM functions")
        function_count = cursor.fetchone()[0]

    logger.info(f"Crawling completed. Visited {len(visited_urls)} pages.")
    logger.info(f"Database content: {app_count} applications, {module_count} modules, {function_count} functions")
    return {
        "message": "Crawling completed successfully.",
        "pages_visited": len(visited_urls),
        "database_content": {
            "applications": app_count,
            "modules": module_count,
            "functions": function_count
        }
    }

def extract_app_info(soup, cursor):
    sidebar_project_name = soup.find('a', class_='sidebar-projectName')
    app_name = sidebar_project_name.text.strip() if sidebar_project_name else "Unknown"
    
    sidebar_project_version = soup.find('div', class_='sidebar-projectVersion')
    version = sidebar_project_version.text.strip() if sidebar_project_version else "Unknown"

    description = ""
    content_div = soup.find('div', id='content')
    if content_div:
        first_p = content_div.find('p')
        if first_p:
            description = first_p.text.strip()

    logger.debug(f"Inserting application: {app_name}, {version}, {description}")
    cursor.execute("""
        INSERT INTO applications (name, version, description) VALUES (?, ?, ?)
    """, (app_name, version, description))
    app_id = cursor.lastrowid

    logger.info(f"Inserted application: {app_name} (ID: {app_id})")
    return {"id": app_id, "name": app_name, "version": version}

def extract_hexdoc_links(soup, base_url, library_path):
    new_links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        # Handle relative URLs
        if not href.startswith(('http://', 'https://')):
            full_url = urljoin(base_url, f'/{library_path}/{href.lstrip("/")}')
        else:
            full_url = href

        parsed_full_url = urlparse(full_url)
        
        # Ensure the link is within the correct domain and library path
        if (parsed_full_url.netloc == urlparse(base_url).netloc and
            parsed_full_url.path.startswith(f'/{library_path}/') and
            not parsed_full_url.path.endswith(('.css', '.js'))):
            
            # Normalize the URL to ensure consistent format
            normalized_url = f"{parsed_full_url.scheme}://{parsed_full_url.netloc}{parsed_full_url.path}"
            if parsed_full_url.query:
                normalized_url += f"?{parsed_full_url.query}"
            if parsed_full_url.fragment:
                normalized_url += f"#{parsed_full_url.fragment}"
            
            new_links.append(normalized_url)
    
    logger.info(f"Found {len(new_links)} relevant links to crawl")
    return new_links

def extract_module_info(soup, url, app_id, cursor):
    # The module name is usually in the first h1 tag
    h1_tag = soup.find('h1')
    if h1_tag:
        module_name = h1_tag.text.strip().split(' –')[0]  # Remove the app name if present
    else:
        module_name = "Unknown Module"
    
    # The module description is usually in the section with id="moduledoc"
    moduledoc = soup.find('section', id='moduledoc')
    description = moduledoc.text.strip() if moduledoc else ""

    logger.debug(f"Inserting module: {module_name}, {url}, {description[:100]}...")
    cursor.execute("""
        INSERT INTO modules (application_id, name, url, description) VALUES (?, ?, ?, ?)
    """, (app_id, module_name, url, description))
    module_id = cursor.lastrowid

    logger.info(f"Inserted module: {module_name} (ID: {module_id})")

    # Extract functions for this module
    functions = extract_functions(soup, module_id, cursor)
    logger.info(f"Extracted {len(functions)} functions for module {module_name}")

    return {"id": module_id, "name": module_name, "url": url, "description": description, "functions": functions}

def extract_functions(soup, module_id, cursor):
    functions = []
    function_sections = soup.find_all('section', class_='detail')
    
    for section in function_sections:
        header = section.find('h1', class_='signature')
        if not header:
            continue

        full_name = header.text.strip()
        name, arity = full_name.split('/', 1) if '/' in full_name else (full_name, '0')
        arity = int(arity)

        summary = ""
        description = ""
        docstring = section.find('section', class_='docstring')
        if docstring:
            summary_p = docstring.find('p')
            if summary_p:
                summary = summary_p.text.strip()
            description = docstring.text.strip()

        logger.debug(f"Inserting function: {name}/{arity}, {summary[:50]}...")
        cursor.execute("""
            INSERT INTO functions (module_id, name, arity, summary, description)
            VALUES (?, ?, ?, ?, ?)
        """, (module_id, name, arity, summary, description))
        function_id = cursor.lastrowid

        # Extract parameters and examples here...

        functions.append({
            "id": function_id,
            "name": name,
            "arity": arity,
            "summary": summary,
            "description": description,
            # Add parameters and examples here...
        })

    return functions

def extract_guide_info(soup, url, app_id, cursor):
    guide_title = soup.find('h1').text.strip() if soup.find('h1') else "Unknown Guide"
    content = soup.find('div', id='content').text.strip() if soup.find('div', id='content') else ""

    logger.debug(f"Inserting guide: {guide_title}, {url}, {content[:100]}...")
    cursor.execute("""
        INSERT INTO guides (application_id, title, url, content) VALUES (?, ?, ?, ?)
    """, (app_id, guide_title, url, content))
    guide_id = cursor.lastrowid

    logger.info(f"Inserted guide: {guide_title} (ID: {guide_id})")
    return {"id": guide_id, "title": guide_title, "url": url, "content": content[:100] + "..."}  # Truncate content for logging