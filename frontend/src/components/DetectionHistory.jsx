/*
  This component shows recent detection records.
  It helps explain that SQLite is saving frame-level detection history.
*/

function DetectionHistory({ history }) {
  return (
    <section className="rounded-md border border-slate-200 bg-white">
      <div className="border-b border-slate-200 px-5 py-4">
        <h2 className="text-base font-bold text-slate-950">
          Recent Detection History
        </h2>
        <p className="mt-1 text-sm text-slate-500">
          Latest webcam frames saved by the backend database.
        </p>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-100 text-left text-slate-600">
            <tr>
              <th className="px-5 py-3 font-semibold">ID</th>
              <th className="px-5 py-3 font-semibold">Faces</th>
              <th className="px-5 py-3 font-semibold">Confidence</th>
              <th className="px-5 py-3 font-semibold">Time</th>
              <th className="px-5 py-3 font-semibold">Source</th>
            </tr>
          </thead>

          <tbody className="divide-y divide-slate-100">
            {history.length === 0 ? (
              <tr>
                <td className="px-5 py-5 text-slate-500" colSpan="5">
                  No detection record is saved yet.
                </td>
              </tr>
            ) : (
              history.map((record) => (
                <tr key={record.id}>
                  <td className="px-5 py-3 font-medium text-slate-900">
                    #{record.id}
                  </td>
                  <td className="px-5 py-3 text-slate-700">
                    {record.face_count}
                  </td>
                  <td className="px-5 py-3 text-slate-700">
                    {record.average_confidence}%
                  </td>
                  <td className="px-5 py-3 text-slate-700">
                    {record.processing_time_ms} ms
                  </td>
                  <td className="px-5 py-3 capitalize text-slate-700">
                    {record.source_type}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export default DetectionHistory;
