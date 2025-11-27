import "./globals.css";

export const metadata = {
  title: "ACCA MCQ Website",
  description: "Practice ACCA MCQs easily",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-100 min-h-screen">
        <nav className="bg-blue-600 text-white p-4 text-xl font-semibold">
          ACCA MCQ Hub — Practice Fast
        </nav>

        <main className="max-w-4xl mx-auto p-5">
          {children}
        </main>

        <footer className="text-center p-4 text-gray-600 border-t mt-6">
          © 2025 ACCA MCQ Hub
        </footer>
      </body>
    </html>
  );
}
