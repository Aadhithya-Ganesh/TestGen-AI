import { Suspense } from "react";
import BackdropLoader from "../utils/BackdropLoader";
import { apiFetch } from "../utils/Fetch";
import { Await, Link, useLoaderData } from "react-router-dom";
import { Clock, Folder } from "lucide-react";
import { formatDate } from "../utils/FormatDate";
import { motion } from "motion/react";

function Jobs() {
  const { jobs } = useLoaderData();

  return (
    <div className="mt-10 flex flex-col gap-5">
      <h1 className="text-2xl font-bold">Jobs</h1>
      <Suspense fallback={<BackdropLoader />}>
        <Await resolve={jobs}>
          {(resolvedJobs) => (
            <div>
              {resolvedJobs.jobs.length == 0 && (
                <div className="border-border text-muted-foreground flex flex-col items-center gap-4 rounded-2xl border p-10 text-center">
                  <Folder className="size-10" />
                  <div>
                    No previous analyses. Start by analyzing a repository.
                  </div>
                </div>
              )}
              {resolvedJobs.jobs.map((job: any) => (
                <motion.div
                  key={job.job_id}
                  className="bg-card border-border rounded-2xl border p-5"
                  whileHover={{ scale: 1.02 }}
                  transition={{ duration: 0.2 }}
                >
                  <Link to={`/jobs/${job.job_id}`}>
                    <div className="mx-2 flex items-center justify-between">
                      <div className="flex flex-col gap-1">
                        <p className="text-lg font-semibold">{job.repo_url}</p>
                        <div className="text-muted-foreground flex items-center gap-3">
                          <Clock className="size-4" />
                          <p>{formatDate(job.created_at)}</p>
                        </div>
                      </div>
                      {!job.analysisComplete && (
                        <div className="border-primary size-5 animate-spin rounded-full border-4 border-t-transparent"></div>
                      )}
                      {job.analysisComplete && (
                        <p className="text-primary font-bold">
                          {job.currentCoverage}%
                        </p>
                      )}
                    </div>
                  </Link>
                </motion.div>
              ))}
            </div>
          )}
        </Await>
      </Suspense>
    </div>
  );
}

export default Jobs;

export async function loader() {
  return {
    jobs: apiFetch("/api/jobs", {
      method: "GET",
    }).then((res) => res.json()),
  };
}
