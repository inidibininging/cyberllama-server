import re

class StringService:
    def remove_at_start(self, str, prefix):
        if not str.startswith(prefix):
            return str
        return str[len(prefix):]
    
    def remove_at_end(self, str, prefix):
        if not str.endswith(prefix):
            return str
        return str[:len(prefix)]

    def trim_parentheses(self, text: str) -> str:
        """
        Remove all substrings enclosed in parentheses, regardless of context.

        Parameters
        ----------
        text : str
            The string to be cleaned.

        Returns
        -------
        str
            The string with every parenthesised fragment removed.

        Example
        -------
        >>> trim_parentheses('Hello (world)! (foo)')
        'Hello ! '
        """
        return re.sub(r'\([^)]*\)', '', text)

    def trim_html_tags(self, text: str) -> str:
        """
        Remove all substrings enclosed in parentheses, regardless of context.

        Parameters
        ----------
        text : str
            The string to be cleaned.

        Returns
        -------
        str
            The string with every parenthesised fragment removed.

        Example
        -------
        >>> trim_parentheses('Hello <world>! <foo>')
        'Hello ! '
        """
        return re.sub(r'\<[^>]*\)', '', text)

    def trim_marked(self, text: str) -> str:
        """
        Remove any substring that is enclosed in:
            ** ... **       (double asterisks)
            *  ...  *       (single asterisks, possibly with surrounding whitespace)

        Additionally removes any dangling asterisks that are not part of a valid pair:
            **like this.
            *like this.
            like this*

        Parameters
        ----------
        text : str
            Input string containing Markdown‑style emphasis markers.

        Returns
        -------
        str
            Cleaned string with the marked sections removed.
        """

        # 1. Remove double‑asterisk blocks (including surrounding whitespace).
        #    The non‑greedy .*? ensures we stop at the next **.
        text = re.sub(r'\s*\*\*.*?\*\*\s*', ' ', text)

        # 2. Remove single‑asterisk blocks (including surrounding whitespace).
        #    We allow optional leading/trailing spaces inside the block.
        text = re.sub(r'\s*\*[^*]*?\*\s*', ' ', text)

        # 3. Remove dangling asterisks that are not part of a pair.
        #    *like this.   -> remove '*like this.'
        #    **like this.  -> remove '**like this.'
        #    like this*    -> remove 'like this*'
        text = re.sub(r'\*\*?[^*]*\.', ' ', text)   # **like this. or *like this.
        text = re.sub(r'[^*]*\*\*?', ' ', text)     # like this* or like this**

        # 4. Collapse any multiple spaces into a single space and strip ends.
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def collapse_trailing_dots(self, text: str) -> str:
        """
        Replace every occurrence of two or more consecutive '.' characters
        with a single '.'.

        Parameters
        ----------
        text : str
            The input string to process.

        Returns
        -------
        str
            The cleaned string with all dot runs collapsed.
        """
        # The regular expression \.{2,} matches any sequence of 2 or more dots.
        return re.sub(r"\.{2,}", " uh ", text)

    def text_has_xml(self, text):
        t = text.lower()
        return "http" in t or\
            "xml" in t or\
            "href" in t or\
            "fontfamily" in t or\
            "verticalalgin" in t or\
            "setnumber" in t or\
            "fontsize" in t or\
            "p style" in t or\
            "TAG" in text

    def contains_html(self, text):
        """
        Detects if the given text contains HTML tags.
        
        Args:
            text (str): The input text to check for HTML content
        
        Returns:
            bool: True if HTML is detected, False otherwise
        """
        # Regex pattern to match HTML tags
        html_pattern = re.compile(r'<[^>]+>', re.IGNORECASE)
        
        # Check if any HTML tags are found in the text
        return bool(html_pattern.search(text))


