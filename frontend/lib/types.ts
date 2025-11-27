export interface Question {
  id: number;
  question: string;
  options: string[];
  correct_option: number | null;
  explanation?: string | null;
  source_file?: string | null;
  page_no?: number | null;
}

export interface UploadResponse {
  status: string;
  message: string;
  saved_count: number;
  total_parsed: number;
}

export interface QuizResponse {
  total: number;
  questions: Question[];
}
