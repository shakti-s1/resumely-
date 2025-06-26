from rest_framework import serializers


class ResumeAnalysisSerializer(serializers.Serializer):
    """
    Serializer for analyzing resume text with AI.
    Accepts either resume_text (string) or resume_file (PDF/DOCX).
    Returns ai_feedback (dict).
    """
    resume_text = serializers.CharField(
        write_only=True, required=False, help_text="Extracted text from the resume to be analyzed.")
    resume_file = serializers.FileField(
        write_only=True, required=False, help_text="Resume file (PDF or DOCX) to be analyzed.")
    ai_feedback = serializers.DictField(
        read_only=True, help_text="Structured AI feedback for the resume.")

    def validate(self, data):
        # Ensure at least one of resume_text or resume_file is provided
        if not data.get('resume_text') and not data.get('resume_file'):
            raise serializers.ValidationError(
                "You must provide either resume_text or resume_file.")
        return data
