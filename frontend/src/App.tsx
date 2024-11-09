import { useState } from 'react'
import { format } from 'date-fns';

interface ScrapeOptions {
  formats?: string[];
  headers?: Record<string, string>;
  includeTags?: string[];
  excludeTags?: string[];
  onlyMainContent?: boolean;
  mobile?: boolean;
  waitFor?: number;
}

interface CrawlRequest {
  url: string;
  excludePaths?: string[];
  includePaths?: string[];
  maxDepth?: number;
  ignoreSitemap?: boolean;
  limit?: number;
  allowBackwardLinks?: boolean;
  allowExternalLinks?: boolean;
  webhook?: string;
  scrapeOptions?: ScrapeOptions;
}

interface PageData {
  html: string;
  markdown: string;
  metadata: Record<string, any>;
}

interface CrawlResponse {
  data: {
    success: boolean;
    status: string;
    completed: number;
    total: number;
    creditsUsed: number;
    expiresAt: string;
    data: PageData[];
  }
}

function App() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [crawlStatus, setCrawlStatus] = useState<CrawlResponse | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    const request: CrawlRequest = {
      url,
      limit: 100,
      excludePaths: [],
      allowBackwardLinks: false,
      scrapeOptions: {
        formats: ['markdown', 'html']
      }
    };

    try {
      const response = await fetch('http://localhost:8000/api/crawl', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setCrawlStatus(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-4xl font-bold text-center mb-8">Website Crawler</h1>
      
      <form onSubmit={handleSubmit} className="mb-8">
        <div className="flex gap-4">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="Enter website URL"
            required
            className="flex-1 px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700"
          />
          <button
            type="submit"
            disabled={loading}
            className={`px-6 py-2 rounded-lg text-white font-medium transition-colors
              ${loading 
                ? 'bg-gray-400 cursor-not-allowed' 
                : 'bg-indigo-600 hover:bg-indigo-700'}`}
          >
            {loading ? 'Crawling...' : 'Start Crawl'}
          </button>
        </div>
      </form>

      {error && (
        <div className="p-4 mb-4 text-red-700 bg-red-100 rounded-lg dark:bg-red-900/50 dark:text-red-300">
          {error}
        </div>
      )}

      {crawlStatus && (
        <div className="mt-4 p-4 border rounded-lg">
          <h2 className="text-xl font-bold mb-4">Crawl Status</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p><strong>Status:</strong> {crawlStatus.data.status}</p>
              <p><strong>Progress:</strong> {crawlStatus.data.completed}/{crawlStatus.data.total}</p>
              <p><strong>Credits Used:</strong> {crawlStatus.data.creditsUsed}</p>
              <p><strong>Expires At:</strong> {crawlStatus.data.expiresAt ? 
                format(new Date(crawlStatus.data.expiresAt), 'PPpp') : 'N/A'}</p>
            </div>
            <div>
              <p><strong>Success:</strong> {crawlStatus.data.success ? 'Yes' : 'No'}</p>
            </div>
          </div>
          
          {crawlStatus.data.data && crawlStatus.data.data.length > 0 && (
            <div className="mt-4">
              <h3 className="text-lg font-bold mb-2">Crawled Pages</h3>
              <div className="space-y-4">
                {crawlStatus.data.data.map((page, index) => (
                  <div key={index} className="border p-4 rounded-lg">
                    <h4 className="font-bold">{page.metadata.title || 'Untitled'}</h4>
                    <p className="text-sm text-gray-600">{page.metadata.url}</p>
                    <div className="mt-2">
                      <details>
                        <summary className="cursor-pointer">View Content</summary>
                        <div className="mt-2 whitespace-pre-wrap">
                          {page.markdown || page.html}
                        </div>
                      </details>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default App
