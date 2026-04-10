import { useParams } from "react-router-dom";

function Job() {
  const { jobId } = useParams();
  return (
    <div>
      Job
      <p>Job ID: {jobId}</p>
    </div>
  );
}

export default Job;
