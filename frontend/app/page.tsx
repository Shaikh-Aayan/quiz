"use client";

import { useEffect, useState } from "react";
import UploadForm from "../components/UploadForm";
import Quiz from "../components/Quiz";
import { fetchQuestions } from "@/lib/api";

export default function Home() {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const data = await fetchQuestions();
      setQuestions(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <div>
      <h1 className="text-3xl font-bold mb-5">🎯 ACCA MCQ Hub</h1>

      <UploadForm onUploaded={load} />

      <section className="mb-6">
        <h2 className="text-xl font-semibold mb-3">📊 Available Questions</h2>
        {loading ? (
          <p className="text-gray-600">Loading questions...</p>
        ) : questions.length === 0 ? (
          <p className="text-gray-600">No parsed questions yet. Upload a PDF to start.</p>
        ) : (
          <p className="text-gray-600">{questions.length} questions in DB. Start a quiz below.</p>
        )}
      </section>

      {questions.length > 0 && (
        <section>
          <h2 className="text-xl font-semibold mb-3">🧠 Quick Quiz</h2>
          <Quiz questions={questions.slice(0, 10)} />
        </section>
      )}
    </div>
  );
}
