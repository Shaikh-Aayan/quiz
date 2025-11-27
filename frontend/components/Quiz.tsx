"use client";
import { useState } from "react";

export default function Quiz({ questions }) {
  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);

  function pick(qid, idx) {
    setAnswers((s) => ({ ...s, [qid]: idx }));
  }

  function submit() {
    setSubmitted(true);
  }

  const score =
    submitted &&
    questions.reduce((acc, q) => {
      const picked = answers[q.id];
      if (picked === undefined) return acc;
      if (q.correct_option !== null && q.correct_option === picked) return acc + 1;
      return acc;
    }, 0);

  return (
    <div className="space-y-4">
      {questions.map((q) => (
        <div key={q.id} className="border p-4 rounded bg-white">
          <div className="font-semibold">{q.question}</div>
          <div className="mt-2 space-y-2">
            {q.options.map((opt, idx) => {
              const isPicked = answers[q.id] === idx;
              const isCorrect = q.correct_option === idx;
              return (
                <label
                  key={idx}
                  className={`flex items-center gap-2 p-2 rounded cursor-pointer ${
                    submitted ? (isCorrect ? "bg-green-50" : isPicked ? "bg-red-50" : "") : "hover:bg-gray-50"
                  }`}
                >
                  <input
                    type="radio"
                    name={String(q.id)}
                    checked={isPicked}
                    onChange={() => pick(q.id, idx)}
                    className="accent-blue-600"
                  />
                  <span>{opt}</span>
                </label>
              );
            })}
          </div>

          {submitted && q.explanation && (
            <div className="mt-2 text-sm text-gray-700">
              <strong>Explanation:</strong> {q.explanation}
            </div>
          )}
        </div>
      ))}

      <div className="flex gap-2">
        <button onClick={submit} className="px-4 py-2 bg-blue-600 text-white rounded">
          Submit
        </button>
        {submitted && <div className="text-lg self-center">Score: {score} / {questions.length}</div>}
      </div>
    </div>
  );
}
