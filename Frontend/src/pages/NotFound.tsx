import { Link, useRouteError, isRouteErrorResponse } from "react-router-dom";
import { useEffect } from "react";

const ErrorPage = () => {
  const error = useRouteError();

  let status = 500;
  let title = "Something went wrong";
  let message = "An unexpected error occurred.";

  if (isRouteErrorResponse(error)) {
    status = error.status;

    if (status === 404) {
      title = "404";
      message = "Oops! Page not found.";
    }

    if (status === 401) {
      title = "Unauthorized";
      message = "You must be logged in to access this page.";
    }

    if (status === 500) {
      title = "Server Error";
      message = "Our server encountered an issue.";
    }

    // Backend-provided message (highest priority)
    if (error.data?.message) {
      message = error.data.message;
    }
  } else if (error instanceof Error) {
    message = error.message;
  }

  useEffect(() => {
    console.error("Route error:", error);
  }, [error]);

  return (
    <div className="bg-background flex min-h-screen items-center justify-center">
      <div className="max-w-md text-center">
        <h1 className="text-foreground mb-4 text-5xl font-bold">{status}</h1>
        <h1 className="text-foreground mb-4 text-5xl font-bold">{title}</h1>
        <p className="text-muted-foreground mb-6 text-xl">{message}</p>

        <Link
          to="/home"
          className="text-primary hover:text-primary/90 underline"
        >
          Return to Home
        </Link>
      </div>
    </div>
  );
};

export default ErrorPage;
