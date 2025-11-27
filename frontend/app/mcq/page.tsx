export default function MCQPage() {
  return (
    <div className="p-6 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">MCQ Quiz</h1>

      <div className="border p-4 rounded">
        <p className="font-medium mb-3">Q1) Sample question yahan aayega...</p>

        <div className="flex flex-col gap-2">
          <label><input type="radio" name="opt" /> Option A</label>
          <label><input type="radio" name="opt" /> Option B</label>
          <label><input type="radio" name="opt" /> Option C</label>
          <label><input type="radio" name="opt" /> Option D</label>
        </div>

        <button className="mt-4 px-4 py-2 bg-blue-500 text-white rounded">
          Next
        </button>
      </div>
    </div>
  );
}
