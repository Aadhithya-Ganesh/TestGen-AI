import { motion } from "motion/react";
import Input from "../components/ui/Input";
import useInput from "../hooks/useInput";
import { validateGithubRepoUrl } from "../utils/FormValidation";
import { GitBranch, Globe, ShieldCheck, Zap } from "lucide-react";
import Select from "../components/ui/Select";
import { useState } from "react";
import Button from "../components/ui/Button";
import { apiFetch } from "../utils/Fetch";
import Cards from "../components/Cards";

function Homepage() {
  const {
    value: urlValue,
    handleBlur: urlBlur,
    handleChange: urlChange,
    error: urlError,
  } = useInput("", validateGithubRepoUrl);

  const [selected, setSelected] = useState<string>("");

  const languages = [
    { label: "Python", value: "python" },
    { label: "Javascript", value: "javascript" },
    { label: "Typescript", value: "typescript" },
    { label: "Java", value: "java" },
    { label: "Go", value: "go" },
    { label: "Rust", value: "rust" },
    { label: "C++", value: "c++" },
    { label: "Ruby", value: "ruby" },
  ];

  const isValid = urlValue && !urlError && selected != "";

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    const token = localStorage.getItem("token");

    if (!token) {
      window.location.assign(
        `https://github.com/login/oauth/authorize?client_id=${import.meta.env.VITE_GITHUB_CLIENT_ID}`,
      );
      return;
    }

    const formdata = new FormData(e.currentTarget);
    const repo_url = formdata.get("url");

    if (!repo_url) {
      return;
    }

    const data = await apiFetch("/api/analyze", {
      method: "POST",
      params: {
        repo_url: String(repo_url),
        language: String(selected),
      },
    }).then((response) => response.json());
  };

  return (
    <div>
      {/* Hero Section */}
      <motion.div
        className="mt-8"
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
      >
        <p className="mx-auto mb-5 w-4/5 text-center text-6xl leading-15 font-bold tracking-wide">
          Generate Unit Tests{" "}
          <span className="text-primary">Automatically</span>
        </p>
        <p className="text-muted-foreground text-center text-lg font-medium">
          Analyze any repository and improve test coverage with AI.
        </p>
      </motion.div>

      {/* Form Card */}
      <motion.form
        className="bg-card border-border m-auto mt-5 flex w-6/8 flex-col gap-5 rounded-2xl border p-10"
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.2, duration: 0.3 }}
        onSubmit={handleSubmit}
      >
        {/* Repo URL Input */}
        <Input
          id="url"
          name="url"
          type="text"
          icon={<Globe />}
          label="Repository URL"
          placeholder="https://github.com/user/repo"
          value={urlValue}
          onChange={urlChange}
          onBlur={urlBlur}
          error={urlError ?? undefined}
        />

        {/* Language Select */}
        <Select
          value={selected}
          label="Language"
          onChange={(value: string) => setSelected(value)}
          placeholder="Select Language"
          options={languages}
        />

        {/* Submit Button */}
        <Button
          disabled={!isValid}
          type="submit"
          className={`mt-4 rounded-lg px-4 py-2 font-semibold text-white transition ${
            isValid
              ? "bg-primary hover:opacity-90"
              : "bg-primary/50 cursor-not-allowed"
          }`}
        >
          Analyze repository
        </Button>
      </motion.form>
      <motion.div
        className="m-auto mt-5 grid w-6/8 grid-cols-3 gap-5"
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ delay: 0.4, duration: 0.3 }}
      >
        <Cards
          heading="Repo Analysis"
          description="Connects to any public GitHub repo, clones it, and maps out your codebase structure automatically."
          icon={<GitBranch className="text-primary" />}
        />
        <Cards
          heading="AI Test Generation"
          description="Generates meaningful unit tests for every file using context-aware AI — not just boilerplate."
          icon={<Zap className="text-primary" />}
        />
        <Cards
          heading="Coverage Reports"
          description="See per-file coverage breakdowns and know exactly where your test gaps are."
          icon={<ShieldCheck className="text-primary" />}
        />
      </motion.div>
    </div>
  );
}

export default Homepage;
