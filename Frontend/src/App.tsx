import { Toaster } from "sonner";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import RootPage from "./pages/RootPage";
import NotFound from "./pages/NotFound";
import Homepage from "./pages/Homepage";
import NavbarLayout from "./pages/NavbarLayout";
import Dashboard from "./pages/Dashboard";
import History from "./pages/History";
import { authLoader, optionalAuthLoader } from "./pages/Auth";

function App() {
  const router = createBrowserRouter([
    {
      path: "/",
      element: <RootPage />,
      errorElement: <NotFound />,
      children: [
        {
          element: <NavbarLayout />,
          loader: optionalAuthLoader,
          children: [
            {
              path: "",
              element: <Homepage />,
            },
            {
              loader: authLoader,
              children: [
                {
                  path: "dashboard",
                  element: <Dashboard />,
                },
                {
                  path: "history",
                  element: <History />,
                },
              ],
            },
          ],
        },
      ],
    },
  ]);

  return (
    <>
      <RouterProvider router={router} />
      <Toaster richColors position="top-right" />
    </>
  );
}

export default App;
