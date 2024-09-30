import React, { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import axios from "axios";
import { Alert, AlertTitle, AlertDescription } from "./components/ui/alert";
import { Terminal } from "lucide-react";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

interface Application {
  id: number;
  name: string;
  version: string;
  description?: string;
}

interface Module {
  id: number;
  name: string;
  description?: string;
}

interface FunctionItem {
  id: number;
  name: string;
  arity: number;
  return_type?: string;
  summary?: string;
  description?: string;
}
interface Parameter {
  id: number;
  name: string;
  type?: string;
  default_value?: string;
  description?: string;
}

interface Example {
  id: number;
  code: string;
  description?: string;
}

interface FunctionItem {
  id: number;
  name: string;
  arity: number;
  return_type?: string;
  summary?: string;
  description?: string;
  parameters: Parameter[];
  examples: Example[];
}

function App() {
  const [url, setUrl] = useState("");
  const [selectedApp, setSelectedApp] = useState<Application | null>(null);
  const [selectedModule, setSelectedModule] = useState<Module | null>(null);

  const scrapeMutation = useMutation({
    mutationFn: async (url: string) => {
      const response = await axios.post("http://localhost:8000/api/scrape", {
        url,
      });
      return response.data;
    },
    onSuccess: () => {
      toast.success("Scraping started!");
      applicationsRefetch();
    },
    onError: (error: any) => {
      toast.error(`Error: ${error.response?.data?.error || error.message}`);
    },
  });

  const {
    data: applications,
    isLoading: applicationsLoading,
    refetch: applicationsRefetch,
  } = useQuery<Application[]>({
    queryKey: ["applications"],
    queryFn: async () => {
      const response = await axios.get("http://localhost:8000/api/applications");
      console.log("Applications data:", response.data);
      return response.data;
    },
  });

  const {
    data: modules,
    isLoading: modulesLoading,
    refetch: modulesRefetch,
  } = useQuery<Module[]>({
    queryKey: ["modules", selectedApp?.id],
    queryFn: async () => {
      if (!selectedApp) return [];
      const response = await axios.get(
        `http://localhost:8000/api/applications/${selectedApp.id}/modules`
      );
      console.log("Modules data:", response.data);
      return response.data;
    },
    enabled: !!selectedApp,
  });

  const {
    data: functions,
    isLoading: functionsLoading,
    error: functionsError,
    refetch: functionsRefetch,
  } = useQuery<FunctionItem[]>({
    queryKey: ["functions", selectedModule?.id],
    queryFn: async () => {
      if (!selectedModule) return [];
      const response = await axios.get(
        `http://localhost:8000/api/modules/${selectedModule.id}/functions`
      );
      console.log("Functions data:", response.data);
      return response.data;
    },
    enabled: !!selectedModule,
  });

  const handleScrape = () => {
    if (!url) {
      toast.error("Please enter a URL.");
      return;
    }
    scrapeMutation.mutate(url);
  };

  return (
    <div className="container mx-auto p-4">
      <ToastContainer />
      <Alert>
        <Terminal className="h-4 w-4" />
        <AlertTitle>HexDoc Scraper</AlertTitle>
        <AlertDescription>
          Enter a HexDoc URL to scrape the documentation.
        </AlertDescription>
      </Alert>

      <div className="mt-8">
        <input
          type="text"
          className="border p-2 w-full"
          placeholder="Enter HexDoc URL"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />
        <button
          className="mt-2 px-4 py-2 bg-blue-500 text-white rounded"
          onClick={handleScrape}
        >
          Start Scraping
        </button>
      </div>

      <h2 className="text-2xl font-bold mt-8 mb-4">Applications</h2>
      {applicationsLoading ? (
        <p>Loading applications...</p>
      ) : applications && applications.length > 0 ? (
        <ul>
          {applications.map((app) => (
            <li
              key={app.id}
              className={`cursor-pointer ${
                selectedApp?.id === app.id ? "font-bold" : ""
              }`}
              onClick={() => {
                setSelectedApp(app);
                setSelectedModule(null);
                modulesRefetch();
              }}
            >
              {app.name} {app.version}
            </li>
          ))}
        </ul>
      ) : (
        <p>No applications found. Try scraping a HexDoc URL first.</p>
      )}

      {selectedApp && (
        <>
          <h2 className="text-2xl font-bold mt-8 mb-4">Modules</h2>
          {modulesLoading ? (
            <p>Loading modules...</p>
          ) : (
            modules && (
              <ul>
                {modules.map((mod) => (
                  <li
                    key={mod.id}
                    className={`cursor-pointer ${
                      selectedModule?.id === mod.id ? "font-bold" : ""
                    }`}
                    onClick={() => {
                      setSelectedModule(mod);
                      functionsRefetch();
                    }}
                  >
                    {mod.name}
                  </li>
                ))}
              </ul>
            )
          )}
        </>
      )}

      {selectedModule && (
        <>
          <h2 className="text-2xl font-bold mt-8 mb-4">Functions</h2>
          {functionsLoading ? (
            <p>Loading functions...</p>
          ) : functionsError ? (
            <p className="text-red-500">Error loading functions: {(functionsError as Error).message}</p>
          ) : functions && functions.length > 0 ? (
            <ul>
              {functions.map((func) => (
                <li key={func.id} className="mb-6">
                  <h3 className="text-xl font-semibold">
                    {func.name}/{func.arity}
                  </h3>
                  {func.summary && <p>{func.summary}</p>}
                  {func.description && <p>{func.description}</p>}

                  {func.parameters.length > 0 && (
                    <div className="mt-2">
                      <h4 className="font-semibold">Parameters:</h4>
                      <ul className="list-disc list-inside">
                        {func.parameters.map((param) => (
                          <li key={param.id}>
                            <strong>{param.name}</strong>
                            {param.type && <span>: {param.type}</span>}
                            {param.description && <p>{param.description}</p>}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {func.examples.length > 0 && (
                    <div className="mt-2">
                      <h4 className="font-semibold">Examples:</h4>
                      {func.examples.map((example) => (
                        <pre
                          key={example.id}
                          className="bg-gray-100 p-2 rounded"
                        >
                          <code>{example.code}</code>
                          {example.description && (
                            <p>{example.description}</p>
                          )}
                        </pre>
                      ))}
                    </div>
                  )}
                </li>
              ))}
            </ul>
          ) : (
            <p>No functions found for this module.</p>
          )}
        </>
      )}
    </div>
  );
}

export default App;
