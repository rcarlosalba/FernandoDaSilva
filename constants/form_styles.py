"""
Fernando Da Silva Forms Styling
Centralized form widget styles using Tailwind CSS classes.
Based on brand colors and existing design patterns.
"""

# ====== BASE INPUT STYLES ======

# Standard text inputs (TextInput, EmailInput, NumberInput, URLInput, etc.)
BASE_INPUT = ("w-full px-4 py-3 border border-neutral-300 rounded-lg "
              "bg-background-cream text-neutral-800 placeholder-neutral-400 "
              "focus:outline-none focus:ring-2 focus:ring-primary-400 focus:border-primary-400 "
              "transition-colors duration-200")

# Password inputs - same as base but with better security styling
PASSWORD_INPUT = ("w-full px-4 py-3 border border-neutral-300 rounded-lg "
                  "bg-background-cream text-neutral-800 placeholder-neutral-400 "
                  "focus:outline-none focus:ring-2 focus:ring-primary-400 focus:border-primary-400 "
                  "transition-colors duration-200")

# Search inputs - with subtle search styling
SEARCH_INPUT = ("w-full px-4 py-3 pl-10 border border-neutral-300 rounded-lg "
                "bg-background-cream text-neutral-800 placeholder-neutral-400 "
                "focus:outline-none focus:ring-2 focus:ring-primary-400 focus:border-primary-400 "
                "transition-colors duration-200")

# ====== SELECT STYLES ======

# Standard select dropdowns
BASE_SELECT = ("w-full px-4 py-3 border border-neutral-300 rounded-lg "
               "bg-background-cream text-neutral-800 "
               "focus:outline-none focus:ring-2 focus:ring-primary-400 focus:border-primary-400 "
               "transition-colors duration-200 appearance-none")

# Multiple select
MULTIPLE_SELECT = ("w-full px-4 py-3 border border-neutral-300 rounded-lg "
                   "bg-background-cream text-neutral-800 "
                   "focus:outline-none focus:ring-2 focus:ring-primary-400 focus:border-primary-400 "
                   "transition-colors duration-200")

# ====== TEXTAREA STYLES ======

# Standard textarea
BASE_TEXTAREA = ("w-full px-4 py-3 border border-neutral-300 rounded-lg "
                 "bg-background-cream text-neutral-800 placeholder-neutral-400 "
                 "focus:outline-none focus:ring-2 focus:ring-primary-400 focus:border-primary-400 "
                 "transition-colors duration-200 resize-vertical")

# Small textarea (for comments, notes)
SMALL_TEXTAREA = "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-brand-primary transition-colors duration-200 resize-vertical min-h-[80px]"

# Large textarea (for descriptions, content)
LARGE_TEXTAREA = "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-brand-primary transition-colors duration-200 resize-vertical min-h-[120px]"

# ====== CHECKBOX & RADIO STYLES ======

# Standard checkbox
BASE_CHECKBOX = "h-4 w-4 text-brand-primary border-gray-300 rounded focus:ring-2 focus:ring-brand-primary transition-colors duration-200"

# Radio button
BASE_RADIO = "h-4 w-4 text-brand-primary border-gray-300 focus:ring-2 focus:ring-brand-primary transition-colors duration-200"

# ====== DATE & TIME INPUTS ======

# Date inputs
DATE_INPUT = "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-brand-primary transition-colors duration-200"

# DateTime inputs
DATETIME_INPUT = "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-brand-primary transition-colors duration-200"

# Time inputs
TIME_INPUT = "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-brand-primary transition-colors duration-200"

# ====== FILE INPUTS ======

# File upload
FILE_INPUT = ("w-full text-sm text-neutral-800 border border-neutral-300 rounded-lg "
              "cursor-pointer bg-background-cream focus:outline-none focus:ring-2 "
              "focus:ring-primary-400 focus:border-primary-400 file:mr-4 file:py-2 file:px-4 "
              "file:rounded-lg file:border-0 file:text-sm file:font-medium "
              "file:bg-primary-500 file:text-background-cream hover:file:bg-primary-600 "
              "transition-colors duration-200")

# Image upload (specific for product images)
IMAGE_INPUT = "w-full text-sm text-gray-900 border border-gray-300 rounded-md cursor-pointer bg-white focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-brand-primary file:mr-4 file:py-2 file:px-4 file:rounded-l-md file:border-0 file:text-sm file:font-medium file:bg-brand-primary file:text-white hover:file:bg-brand-secondary transition-colors duration-200"

# ====== RANGE & SLIDER INPUTS ======

# Range slider
RANGE_INPUT = "w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider-thumb:appearance-none slider-thumb:h-4 slider-thumb:w-4 slider-thumb:rounded-full slider-thumb:bg-brand-primary slider-thumb:cursor-pointer"

# ====== SPECIAL INPUTS ======

# Currency/Money inputs (for prices)
CURRENCY_INPUT = "w-full pl-8 pr-3 py-2 border border-gray-300 rounded-md shadow-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-brand-primary transition-colors duration-200"

# SKU/Code inputs (for product codes)
CODE_INPUT = "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-gray-900 placeholder-gray-400 font-mono text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-brand-primary transition-colors duration-200"

# Quantity inputs (for product quantities)
QUANTITY_INPUT = "w-20 px-3 py-2 border border-gray-300 rounded-md shadow-sm text-gray-900 text-center focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-brand-primary transition-colors duration-200"

# Phone number inputs
PHONE_INPUT = "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-brand-primary focus:border-brand-primary transition-colors duration-200"

# ====== DISABLED STATES ======

# Disabled input
DISABLED_INPUT = "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm text-gray-500 bg-gray-50 cursor-not-allowed"

# Disabled select
DISABLED_SELECT = "w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm bg-gray-50 text-gray-500 cursor-not-allowed appearance-none"

# ====== ERROR STATES ======

# Input with error
ERROR_INPUT = "w-full px-3 py-2 border border-red-300 rounded-md shadow-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 transition-colors duration-200"

# Select with error
ERROR_SELECT = "w-full px-3 py-2 border border-red-300 rounded-md shadow-sm bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 transition-colors duration-200 appearance-none"

# Textarea with error
ERROR_TEXTAREA = "w-full px-3 py-2 border border-red-300 rounded-md shadow-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 transition-colors duration-200 resize-vertical"

# ====== SUCCESS STATES ======

# Input with success
SUCCESS_INPUT = "w-full px-3 py-2 border border-green-300 rounded-md shadow-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors duration-200"

# Select with success
SUCCESS_SELECT = "w-full px-3 py-2 border border-green-300 rounded-md shadow-sm bg-white text-gray-900 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors duration-200 appearance-none"

# ====== BUTTON STYLES (for form buttons) ======

# Primary button (submit, save)
PRIMARY_BUTTON = "w-full sm:w-auto px-6 py-2 bg-brand-primary text-white font-medium rounded-md shadow-sm hover:bg-brand-secondary focus:outline-none focus:ring-2 focus:ring-brand-primary focus:ring-offset-2 transition-colors duration-200"

# Secondary button (cancel, back)
SECONDARY_BUTTON = "w-full sm:w-auto px-6 py-2 bg-gray-100 text-gray-700 font-medium rounded-md shadow-sm border border-gray-300 hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors duration-200"

# Danger button (delete, remove)
DANGER_BUTTON = "w-full sm:w-auto px-6 py-2 bg-red-600 text-white font-medium rounded-md shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors duration-200"

# ====== FORM LAYOUT HELPERS ======

# Form group container
FORM_GROUP = "mb-4"

# Form row (for side-by-side fields)
FORM_ROW = "grid grid-cols-1 md:grid-cols-2 gap-4"

# Form section (for grouped fields with header)
FORM_SECTION = "border-t border-gray-200 pt-6 mt-6"

# Label styles (though usually handled in templates)
FORM_LABEL = "block text-sm font-medium text-gray-700 mb-1"
REQUIRED_LABEL = "block text-sm font-medium text-gray-700 mb-1 after:content-['*'] after:text-red-500 after:ml-1"

# Help text
HELP_TEXT = "mt-1 text-sm text-gray-500"

# Radio select widget (for RadioSelect)
RADIO_SELECT = "space-y-2"

# Individual radio option in RadioSelect
RADIO_OPTION = "flex items-center"

# Radio input in RadioSelect
RADIO_SELECT_INPUT = "h-4 w-4 text-brand-primary border-gray-300 focus:ring-2 focus:ring-brand-primary transition-colors duration-200 mr-3"

# Radio label in RadioSelect
RADIO_SELECT_LABEL = "text-sm text-gray-700 cursor-pointer"

# ====== CONVENIENCE MAPPINGS ======

# Quick access mapping for common Django field types
FIELD_MAPPING = {
    'CharField': BASE_INPUT,
    'EmailField': BASE_INPUT,
    'URLField': BASE_INPUT,
    'IntegerField': BASE_INPUT,
    'DecimalField': CURRENCY_INPUT,
    'TextField': BASE_TEXTAREA,
    'PasswordField': PASSWORD_INPUT,
    'DateField': DATE_INPUT,
    'DateTimeField': DATETIME_INPUT,
    'TimeField': TIME_INPUT,
    'BooleanField': BASE_CHECKBOX,
    'FileField': FILE_INPUT,
    'ImageField': IMAGE_INPUT,
    'ChoiceField': BASE_SELECT,
    'ModelChoiceField': BASE_SELECT,
    'ModelMultipleChoiceField': MULTIPLE_SELECT,
    'RadioSelect': RADIO_SELECT,
}

# ====== FORM_STYLES DICTIONARY ======

# Main dictionary for easy access to all form styles
FORM_STYLES = {
    'text': BASE_INPUT,
    'email': BASE_INPUT,
    'url': BASE_INPUT,
    'number': BASE_INPUT,
    'password': PASSWORD_INPUT,
    'search': SEARCH_INPUT,
    'select': BASE_SELECT,
    'multiple_select': MULTIPLE_SELECT,
    'textarea': BASE_TEXTAREA,
    'small_textarea': SMALL_TEXTAREA,
    'large_textarea': LARGE_TEXTAREA,
    'checkbox': BASE_CHECKBOX,
    'radio': BASE_RADIO,
    'date': DATE_INPUT,
    'datetime': DATETIME_INPUT,
    'time': TIME_INPUT,
    'file': FILE_INPUT,
    'image': IMAGE_INPUT,
    'range': RANGE_INPUT,
    'currency': CURRENCY_INPUT,
    'code': CODE_INPUT,
    'quantity': QUANTITY_INPUT,
    'phone': PHONE_INPUT,
    'disabled': DISABLED_INPUT,
    'disabled_select': DISABLED_SELECT,
    'error': ERROR_INPUT,
    'error_select': ERROR_SELECT,
    'error_textarea': ERROR_TEXTAREA,
    'success': SUCCESS_INPUT,
    'success_select': SUCCESS_SELECT,
    'primary_button': PRIMARY_BUTTON,
    'secondary_button': SECONDARY_BUTTON,
    'danger_button': DANGER_BUTTON,
    'form_group': FORM_GROUP,
    'form_row': FORM_ROW,
    'form_section': FORM_SECTION,
    'form_label': FORM_LABEL,
    'required_label': REQUIRED_LABEL,
    'help_text': HELP_TEXT,
    'radio_select': RADIO_SELECT,
    'radio_option': RADIO_OPTION,
    'radio_select_input': RADIO_SELECT_INPUT,
    'radio_select_label': RADIO_SELECT_LABEL,
}
