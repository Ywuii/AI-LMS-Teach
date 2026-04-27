export interface LessonPlanConfig {
  chapter: ChapterOption | null;
  sectionTitle: string;
  studentLevel: string;
  classHours: number;
  teachingStyle: string;
}

export interface ChapterOption {
  id: number;
  label: string;
  value: string;
}