# Contributing to CS Archive

Help us build the ultimate knowledge base for Computer Science students and curious minds.

## How to Contribute

1.  **Fork the repository** on GitHub.
2.  **Add your resource** to the appropriate JSON file in the `data/` directory:
    *   `skills.json`: For new CS concepts or skills.
    *   `resources.json`: For external tutorials, courses, and documentation.
    *   `archive-gems.json`: For rare/interesting finds from Archive.org.
    *   `selfhosted.json`: For essential self-hosted tools.
    *   `repos.json`: For must-have GitHub repositories.
3.  **Validate your JSON**. Ensure the syntax is correct.
4.  **Submit a Pull Request** with a description of what you added.

## Guidelines

*   **Quality over Quantity**: Only add high-quality, free (or high value) resources.
*   **No Spam**: Affiliate links or low-effort content will be rejected.
*   **Tags**: Add relevant tags to help with the keyword search.

## Structure

Each entry should generally follow this schema:

```json
{
  "name": "Item Name",
  "category": "Category",
  "description": "Brief, useful description.",
  "url": "https://...",
  "tags": ["tag1", "tag2"]
}
```

Thank you for contributing to the archive!
