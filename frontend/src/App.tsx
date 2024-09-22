import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Alert, AlertTitle, AlertDescription } from "./components/ui/alert";
import { Terminal } from "lucide-react";

function App() {
  return (
    <div className="container mx-auto p-4">
      <Alert>
      <Terminal className="h-4 w-4" />
      <AlertTitle>Heads up!</AlertTitle>
      <AlertDescription>
        You can add components to your app using the cli.
      </AlertDescription>
    </Alert>
    </div>
  );
}

export default App;
