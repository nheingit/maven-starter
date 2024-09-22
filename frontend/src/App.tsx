import React from "react";
import { useQuery } from "@tanstack/react-query";
import { Alert, AlertTitle, AlertDescription } from "./components/ui/alert";
import { Terminal } from "lucide-react";

interface BlogPost {
  id: number;
  title: string;
  content: string;
}

const fetchBlogPosts = async (): Promise<BlogPost[]> => {
  const response = await fetch("http://localhost:8000/api/blog");
  if (!response.ok) {
    throw new Error("Network response was not ok");
  }
  return response.json();
};

function App() {
  const { data: blogPosts, isLoading, error } = useQuery<BlogPost[], Error>({
    queryKey: ["blogPosts"],
    queryFn: fetchBlogPosts,
  });

  return (
    <div className="container mx-auto p-4">
      <Alert>
        <Terminal className="h-4 w-4" />
        <AlertTitle>Heads up!</AlertTitle>
        <AlertDescription>
          You can add components to your app using the cli.
        </AlertDescription>
      </Alert>

      <h1 className="text-2xl font-bold mt-8 mb-4">Blog Posts</h1>
      
      {isLoading && <p>Loading blog posts...</p>}
      
      {error && <p className="text-red-500">Error: {error.message}</p>}
      
      {blogPosts && blogPosts.map((post) => (
        <div key={post.id} className="mb-6">
          <h2 className="text-xl font-semibold">{post.title}</h2>
          <p className="mt-2">{post.content}</p>
        </div>
      ))}
    </div>
  );
}

export default App;
