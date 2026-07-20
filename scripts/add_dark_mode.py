import os
import re

directories = ['templates', 'accounts/templates', 'doctor/templates', 'assistant/templates']

replacements = {
    r'\bbg-white\b': 'bg-white dark:bg-gray-800',
    r'\btext-gray-900\b': 'text-gray-900 dark:text-gray-100',
    r'\btext-gray-800\b': 'text-gray-800 dark:text-gray-200',
    r'\btext-gray-700\b': 'text-gray-700 dark:text-gray-300',
    r'\btext-gray-600\b': 'text-gray-600 dark:text-gray-400',
    r'\bbg-gray-50\b': 'bg-gray-50 dark:bg-gray-900',
    r'\bbg-gray-100\b': 'bg-gray-100 dark:bg-gray-900',
    r'\bborder-gray-200\b': 'border-gray-200 dark:border-gray-700',
    r'\bborder-gray-300\b': 'border-gray-300 dark:border-gray-600',
    r'\bbg-blue-50\b': 'bg-blue-50 dark:bg-blue-900 dark:bg-opacity-30',
    r'\bhover:bg-gray-50\b': 'hover:bg-gray-50 dark:hover:bg-gray-700',
    r'\bhover:bg-gray-100\b': 'hover:bg-gray-100 dark:hover:bg-gray-700',
    r'\bfrom-gray-50\b': 'from-gray-50 dark:from-gray-900',
    r'\bto-blue-50\b': 'to-blue-50 dark:to-gray-900',
    r'\bfrom-blue-50\b': 'from-blue-50 dark:from-gray-900',
    r'\bto-teal-100\b': 'to-teal-100 dark:to-gray-900',
}

def process_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    original_content = content
    for pattern, replacement in replacements.items():
        # check if it's already there to prevent duplication
        if replacement not in content:
            # We only want to replace inside class="..." or class='...' attributes to avoid modifying other things.
            # But tailwind classes in Django templates can sometimes be outside, but mostly inside class="".
            # Simple approach: just replace the pattern globally. The risk is low for these specific strings.
            # However, to avoid "bg-white dark:bg-gray-800 dark:bg-gray-800" if ran multiple times:
            escaped_replacement = replacement.replace(':', r'\:')
            content = re.sub(pattern + r'(?! dark:)', replacement, content)

    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Updated {filepath}")

for directory in directories:
    if not os.path.exists(directory):
        continue
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                process_file(filepath)

print("Done processing templates.")
