import { useParams } from "react-router-dom";
import { motion, AnimatePresence } from "motion/react";
import { useEffect, useState, useRef } from "react";
import { apiFetch } from "../utils/Fetch";
import { CheckCircle, GitPullRequest, XCircle, Loader2 } from "lucide-react";
import DiffViewer from "../components/DiffViewer";
import { toast } from "sonner";

type Status = "IN-PROGRESS" | "FAILED" | "SUCCEEDED" | null;

const StatusIcon = ({ status }: { status: Status }) => {
  if (status === "SUCCEEDED")
    return (
      <CheckCircle className="text-primary animate-in fade-in zoom-in h-5 w-5 duration-300" />
    );
  if (status === "FAILED")
    return (
      <XCircle className="animate-in fade-in zoom-in h-5 w-5 text-red-500 duration-300" />
    );
  return (
    <div className="border-primary size-5 animate-spin rounded-full border-4 border-t-transparent" />
  );
};

function Job() {
  const { jobId } = useParams();

  const [job, setJob] = useState<any>(null);
  const [showDetails, setShowDetails] = useState(false);
  const [prLoading, setPrLoading] = useState(false);
  const prPollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // 🔁 Main job polling
  useEffect(() => {
    if (!jobId) return;

    let interval: ReturnType<typeof setInterval> | null = null;

    const fetchJob = async () => {
      try {
        const res = await apiFetch(`/api/jobs/${jobId}`);
        const data = await res.json();
        setJob(data);

        const done =
          data.jobComplete === "SUCCEEDED" || data.jobComplete === "FAILED";
        if (done && interval) {
          clearInterval(interval);
          interval = null;
        }
      } catch (err) {
        console.error("Polling error:", err);
      }
    };

    fetchJob();
    interval = setInterval(fetchJob, 2000);
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [jobId]);

  // ⏱️ Delay transition after repo is cloned
  useEffect(() => {
    if (job?.repoCloned === "SUCCEEDED") {
      const timer = setTimeout(() => setShowDetails(true), 2000);
      return () => clearTimeout(timer);
    }
  }, [job?.repoCloned]);

  // 🔁 PR polling
  const startPrPolling = () => {
    if (prPollRef.current) return;
    prPollRef.current = setInterval(async () => {
      try {
        const res = await apiFetch(`/api/jobs/${jobId}`);
        const data = await res.json();
        setJob(data);
        if (data.prCreated) {
          clearInterval(prPollRef.current!);
          prPollRef.current = null;
          setPrLoading(false);
          toast.success("Pull request created successfully!");
        }
      } catch (err) {
        console.error("PR polling error:", err);
      }
    }, 2000);
  };

  useEffect(() => {
    return () => {
      if (prPollRef.current) clearInterval(prPollRef.current);
    };
  }, []);

  const handleCreatePR = async () => {
    try {
      setPrLoading(true);
      const res = await apiFetch(`/api/jobs/create_pull_request/${jobId}`, {
        method: "POST",
      });
      if (!res.ok) {
        setPrLoading(false);
        toast.error("Failed to create pull request.");
        return;
      }
      startPrPolling();
    } catch (err) {
      console.error(err);
      setPrLoading(false);
      toast.error("An error occurred while creating the pull request.");
    }
  };

  const coverage =
    job?.finalCoverage === 0 ? job?.currentCoverage : job?.finalCoverage;

  const getColor = () => {
    if (coverage < 30) return "bg-red-500";
    if (coverage <= 80) return "bg-yellow-400";
    return "bg-green-500";
  };

  const jobComplete = job?.jobComplete === "SUCCEEDED";
  const jobFailed = job?.jobComplete === "FAILED";
  const prDone = job?.prCreated;

  return (
    <div>
      <AnimatePresence>
        {showDetails && (
          <motion.div
            key="details"
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 20, opacity: 0 }}
            className="flex flex-col gap-10"
          >
            {/* Header */}
            <div className="bg-card border-border flex items-center justify-between rounded-2xl border p-8">
              <div>
                <p className="text-xl font-bold">{job?.repo_url}</p>
                <p className="tracking-widest">
                  {job?.language?.toUpperCase()}
                </p>
              </div>
              <div>
                {jobComplete && (
                  <CheckCircle className="h-8 w-8 text-green-500" />
                )}
                {jobFailed && <XCircle className="h-8 w-8 text-red-500" />}
                {!jobComplete && !jobFailed && (
                  <div className="border-primary size-8 animate-spin rounded-full border-4 border-t-transparent" />
                )}
              </div>
            </div>

            {/* Overview */}
            {job?.currentCoverage != 0 && (
              <div>
                <p className="mb-5 ml-5 text-lg font-bold">Overview</p>
                <div className="bg-card border-border rounded-2xl border p-6">
                  <p className="text-3xl font-bold">
                    {job?.finalCoverage == 0
                      ? job?.currentCoverage
                      : job?.finalCoverage}
                  </p>
                  <p className="text-muted-foreground mt-2 text-sm">
                    {job?.finalCoverage == 0
                      ? "Current Coverage"
                      : "Overall Test Coverage"}
                  </p>
                  <div className="bg-muted mt-4 h-4 w-full rounded-full">
                    <div
                      className={`${getColor()} h-4 rounded-full transition-all duration-500`}
                      style={{ width: `${coverage}%` }}
                    />
                  </div>
                </div>
              </div>
            )}

            {/* File Coverage */}
            <div>
              <p className="mb-5 ml-5 text-lg font-bold">File Coverage</p>
              <div className="border-border bg-card overflow-hidden rounded-2xl border">
                <div className="text-muted-foreground border-border grid grid-cols-2 border-b px-6 py-4 text-sm font-medium">
                  <p>File</p>
                  <p className="text-right">Coverage</p>
                </div>
                {job?.files?.length === 0 && (
                  <p className="text-muted-foreground p-6 text-center text-sm">
                    No files found in the repository.
                  </p>
                )}
                {job?.files?.map((file: any, index: number) => (
                  <div
                    key={index}
                    className="border-border grid grid-cols-2 items-center border-b px-6 py-4 last:border-none"
                  >
                    <p className="truncate font-mono text-sm">
                      {file.filename}
                    </p>
                    <div className="flex items-center justify-end gap-4">
                      <p className="text-sm font-medium">{file.coverage}%</p>
                      <div className="bg-muted h-2 w-32 overflow-hidden rounded-full">
                        <div
                          className={`h-2 rounded-full transition-all ${
                            file.coverage < 30
                              ? "bg-red-500"
                              : file.coverage <= 80
                                ? "bg-yellow-500"
                                : "bg-green-500"
                          }`}
                          style={{ width: `${file.coverage}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <DiffViewer tests={job?.tests || []} />

            {/* PR Button */}
            {jobComplete && (
              <div className="flex flex-col gap-3">
                {prDone ? (
                  <div className="bg-card border-border flex items-center justify-between rounded-2xl border p-6">
                    <div className="flex items-center gap-3">
                      <div className="flex h-10 w-10 items-center justify-center rounded-full bg-green-500/10">
                        <CheckCircle className="h-5 w-5 text-green-500" />
                      </div>
                      <div>
                        <p className="text-sm font-semibold">
                          Pull Request Created
                        </p>
                        <p className="text-muted-foreground text-xs">
                          Your tests have been pushed to a new branch
                        </p>
                      </div>
                    </div>
                    {job?.prUrl && (
                      <a
                        href={job.prUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-2 rounded-lg bg-green-500/10 px-4 py-2 text-sm font-medium text-green-500 transition hover:bg-green-500/20"
                      >
                        <GitPullRequest className="h-4 w-4" />
                        View PR
                      </a>
                    )}
                  </div>
                ) : (
                  <button
                    type="button"
                    onClick={handleCreatePR}
                    disabled={prLoading}
                    className={`bg-card border-border flex w-full items-center justify-between rounded-2xl border p-6 transition ${
                      prLoading
                        ? "cursor-not-allowed opacity-60"
                        : "hover:border-primary cursor-pointer"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className="bg-primary/10 flex h-10 w-10 items-center justify-center rounded-full">
                        {prLoading ? (
                          <Loader2 className="text-primary h-5 w-5 animate-spin" />
                        ) : (
                          <GitPullRequest className="text-primary h-5 w-5" />
                        )}
                      </div>
                      <div className="text-left">
                        <p className="text-sm font-semibold">
                          {prLoading
                            ? "Creating Pull Request..."
                            : "Create Pull Request"}
                        </p>
                        <p className="text-muted-foreground text-xs">
                          {prLoading
                            ? "Pushing changes to GitHub"
                            : "Push generated tests to a new branch"}
                        </p>
                      </div>
                    </div>
                    {!prLoading && (
                      <span className="text-muted-foreground text-xs">→</span>
                    )}
                  </button>
                )}
              </div>
            )}

            {/* Failed state */}
            {jobFailed && (
              <div className="bg-card border-border flex items-center gap-3 rounded-2xl border p-6">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-red-500/10">
                  <XCircle className="h-5 w-5 text-red-500" />
                </div>
                <div>
                  <p className="text-sm font-semibold">Job Failed</p>
                  <p className="text-muted-foreground text-xs">
                    Something went wrong during test generation
                  </p>
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Loading card */}
      <AnimatePresence>
        {!showDetails && (
          <motion.div
            key="loader"
            className="mt-50"
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: 20, opacity: 0 }}
          >
            <div className="border-border bg-card m-auto w-2/5 rounded-2xl border p-10">
              <p className="mb-10 text-2xl font-bold">Analyzing Repository</p>
              <div className="flex flex-col gap-5">
                <div className="flex items-center justify-between">
                  <p>Creating Sandbox Environment</p>
                  <StatusIcon status={job?.containerCreated} />
                </div>
                <div className="flex items-center justify-between">
                  <p>Cloning Repo</p>
                  <StatusIcon status={job?.repoCloned} />
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default Job;
