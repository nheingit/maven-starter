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

    with get_db() as conn:
        cursor = conn.cursor()
        
        while to_visit:
            current_url = to_visit.pop(0)
            if current_url in visited_urls:
                continue

            visited_urls.add(current_url)
            logger.info(f"Scraping: {current_url}")

            try:
                response = requests.get(current_url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')

                if current_url == url:
                    # This is the main page
                    app_info = extract_app_info(soup, cursor)
                    logger.info(f"Extracted application info: {app_info}")
                
                new_links = extract_hexdoc_links(soup, base_url, library_path)
                logger.info(f"Extracted {len(new_links)} new links to visit")
                to_visit.extend([link for link in new_links if link not in visited_urls])

                if f'/{library_path}/' in current_url:
                    if 'modules' in current_url:
                        module_info = extract_module_info(soup, current_url, app_info['id'], cursor)
                        logger.info(f"Extracted module info: {module_info}")
                        
                        # Log function information
                        function_sections = soup.find_all('section', class_='function')
                        logger.info(f"Found {len(function_sections)} function sections")
                        for func_section in function_sections:
                            func_info = extract_function_info(func_section, module_info['id'], cursor)
                            logger.info(f"Extracted function info: {func_info}")
                    elif any(keyword in current_url for keyword in ['guides', 'readme', 'extras']):
                        guide_info = extract_guide_info(soup, current_url, app_info['id'], cursor)
                        logger.info(f"Extracted guide info: {guide_info}")

                # Add a small delay to avoid overwhelming the server
                time.sleep(0.5)

            except requests.RequestException as e:
                logger.error(f"Error accessing the URL {current_url}: {e}")

        conn.commit()

    logger.info(f"Crawling completed. Visited {len(visited_urls)} pages.")
    return {"message": "Crawling completed successfully.", "pages_visited": len(visited_urls)}

def extract_app_info(soup, cursor):
    sidebar_project_name = soup.find('a', class_='sidebar-projectName')
    app_name = sidebar_project_name.text.strip() if sidebar_project_name else "Unknown"
    
    sidebar_project_version = soup.find('div', class_='sidebar-projectVersion')
    version = sidebar_project_version.text.strip() if sidebar_project_version else "Unknown"

    description = ""
    reactor_h1 = soup.find('h1', string=app_name)
    if reactor_h1:
        description_p = reactor_h1.find_next('p')
        if description_p:
            description = description_p.text.strip()

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
    module_name = soup.find('h1').text.strip() if soup.find('h1') else "Unknown Module"
    description = soup.find('section', class_='docstring').text.strip() if soup.find('section', class_='docstring') else ""

    cursor.execute("""
        INSERT INTO modules (application_id, name, url, description) VALUES (?, ?, ?, ?)
    """, (app_id, module_name, url, description))
    module_id = cursor.lastrowid

    logger.info(f"Inserted module: {module_name} (ID: {module_id})")
    return {"id": module_id, "name": module_name, "url": url, "description": description}

def extract_function_info(func_section, module_id, cursor):
    header = func_section.find('h2')
    if not header:
        return None

    name_arity = header.text.strip().split('/')
    name = name_arity[0]
    arity = int(name_arity[1]) if len(name_arity) > 1 else 0

    summary = func_section.find('p').text.strip() if func_section.find('p') else ""
    description = func_section.find('section', class_='docstring').text.strip() if func_section.find('section', class_='docstring') else ""

    cursor.execute("""
        INSERT INTO functions (module_id, name, arity, summary, description)
        VALUES (?, ?, ?, ?, ?)
    """, (module_id, name, arity, summary, description))
    function_id = cursor.lastrowid

    logger.info(f"Inserted function: {name}/{arity} (ID: {function_id})")

    parameters = []
    examples = []

    # Extract parameters
    params_section = func_section.find('section', class_='params')
    if params_section:
        param_items = params_section.find_all('li')
        for param in param_items:
            param_name = param.find('span', class_='name').text.strip()
            param_type = param.find('span', class_='type').text.strip() if param.find('span', class_='type') else ""
            param_desc = param.find('p').text.strip() if param.find('p') else ""
            
            cursor.execute("""
                INSERT INTO parameters (function_id, name, type, description)
                VALUES (?, ?, ?, ?)
            """, (function_id, param_name, param_type, param_desc))
            parameters.append({"name": param_name, "type": param_type, "description": param_desc})

    # Extract examples
    examples_section = func_section.find('section', class_='examples')
    if examples_section:
        example_blocks = examples_section.find_all('pre')
        for example in example_blocks:
            code = example.text.strip()
            description = example.find_previous_sibling('p').text.strip() if example.find_previous_sibling('p') else ""
            
            cursor.execute("""
                INSERT INTO examples (function_id, code, description)
                VALUES (?, ?, ?)
            """, (function_id, code, description))
            examples.append({"code": code, "description": description})

    return {
        "id": function_id,
        "name": name,
        "arity": arity,
        "summary": summary,
        "description": description,
        "parameters": parameters,
        "examples": examples
    }

def extract_guide_info(soup, url, app_id, cursor):
    guide_title = soup.find('h1').text.strip() if soup.find('h1') else "Unknown Guide"
    content = soup.find('div', id='content').text.strip() if soup.find('div', id='content') else ""

    cursor.execute("""
        INSERT INTO guides (application_id, title, url, content) VALUES (?, ?, ?, ?)
    """, (app_id, guide_title, url, content))
    guide_id = cursor.lastrowid

    logger.info(f"Inserted guide: {guide_title} (ID: {guide_id})")
    return {"id": guide_id, "title": guide_title, "url": url, "content": content[:100] + "..."}  # Truncate content for logging
