editor -- somewhat generic app for a markdown-like editor

This app allows you to create a textbox that allows markdown-like syntax for editing documents.  It supports the following features:
  - Markdown-like syntax with a focus on article editing
  - Formatting help page
  - Image upload, with support for left/right/center alignment
  - Video embeds
  - Footnotes

General Setup:
  - Include the editor/scss/editor.scss file in your site's SCSS.
  - You also probably to either include footnotes.scss, or write up custom SCSS to replace it.
  - Include editor.urls in your urlconf

Using the editor:
- Use editor.fields.EditorTextField as for django model field that will store the edited text
- Use this template code to display the field:
  {% include "editor/fieldset.html" with field=field %}
- Also include this code somewhere towards the bottom of the page:
  {% include "editor/preview-modal.html" %}

Configuration:
- Use the EDITOR_CONFIG settings variable to customize the editor
- TODO explain various settings
