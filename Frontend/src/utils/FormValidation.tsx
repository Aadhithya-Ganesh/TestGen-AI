const GITHUB_REGEX =
  /^https:\/\/github\.com\/[a-zA-Z0-9-]+\/[a-zA-Z0-9._-]+\/?$/;

export const validateGithubRepoUrl = (value: string): string | null => {
  if (!value) return "Repository URL is required";

  if (!GITHUB_REGEX.test(value)) {
    return "Invalid GitHub repository URL";
  }

  return null;
};
