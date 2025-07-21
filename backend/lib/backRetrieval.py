import re

class backRetrieval:
    def __init__(self, keyword_generator):
        """
        keyword_generator must be callable: keyword_generator(user_prompt) -> list of keywords
        """
        if not callable(keyword_generator):
            raise ValueError("keyword_generator must be callable.")
        self.keyword_generator = keyword_generator
        self.regulation_sections = []

    def load_regulations(self, file_path, section_pattern=r'^\d+\..*$'):
        """
        Load regulations as a list of sections based on section headings (regex pattern).
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
        # Split by section headings using regex (e.g., '1.', '2.3', etc.)
        split_regex = re.compile(f'({section_pattern})', re.MULTILINE)
        parts = split_regex.split(text)
        self.regulation_sections = []
        for i in range(1, len(parts), 2):
            header = parts[i].strip()
            body = parts[i+1].strip() if i+1 < len(parts) else ""
            self.regulation_sections.append({'header': header, 'body': body})

    def search_with_prompt(self, user_prompt):
        """
        Use AI to generate keywords, then search for matching sections.
        """
        if not self.regulation_sections:
            raise ValueError("Regulations not loaded.")

        keywords = self.keyword_generator(user_prompt)
        matches = []

        for section in self.regulation_sections:
            section_text = f"{section['header']}\n{section['body']}".lower()
            if any(kw.lower() in section_text for kw in keywords):
                matches.append(section)

        return matches
