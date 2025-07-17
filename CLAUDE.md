# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FDS (Fernando Da Silva) is a Django 4.2.19 web application for a personal/professional website with user management, blog, courses, and newsletter functionality. The project uses TailwindCSS for styling and includes a custom user authentication system.

## Architecture

### Django Apps Structure
- **accounts**: Custom user authentication with email-based login and user profiles
- **public**: Main public-facing website pages
- **blog**: Blog functionality (basic structure)
- **courses**: Course management system (basic structure)
- **dashboard**: Admin/user dashboard (basic structure)  
- **newsletter**: Newsletter subscription system (basic structure)
- **core**: Main Django configuration and settings

### Key Components
- **Custom User Model**: `accounts.User` with email as username field and role-based permissions
- **User Profiles**: One-to-one relationship with User model for additional user information
- **Role System**: Hierarchical user roles (Subscriber, Member, Student, Assistant, Manager)
- **Settings Structure**: Split into base.py, local.py, and production.py

## Development Commands

### Django Commands
```bash
# Run development server
python manage.py runserver

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Django shell
python manage.py shell
```

### TailwindCSS Commands
```bash
# Navigate to tailwind directory first
cd tailwind/

# Build CSS for production
npm run build

# Watch for changes during development
npm run dev

# Create minified CSS
npm run minify
```

## Environment Configuration

The project uses django-environ for environment variables. Create `.env.local` file with:
- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `EMAIL_HOST_PASSWORD`: Email service password for Mailtrap

## Settings Configuration

- **Development**: Uses `core.settings.local` (default in manage.py)
- **Production**: Uses `core.settings.production` (commented out in manage.py)
- **Database**: SQLite for development, configurable via DATABASE_URL environment variable

## URL Structure

- `/`: Public website home page
- `/gestion/`: Django admin interface
- `/cuentas/`: User account management (login, register, profile)
- `/__reload__/`: Browser reload middleware (development only)

## Authentication System

- Email-based authentication instead of username
- Custom User model with role-based permissions
- Automatic Profile creation via Django signals
- User roles: Subscriber (default), Member, Student, Assistant, Manager

## Static Files and Media

- **Static files**: `/static/` directory with CSS, JS, and images
- **Media files**: `/media/` directory for user uploads
- **Templates**: `/templates/` with Django form templates customization

## Testing

Use Django's built-in testing framework:
```bash
python manage.py test
python manage.py test app_name
```

## Browser Reload

The project includes `django_browser_reload` for automatic page refresh during development.

## Development Rules and Conventions

### Django Development Rules
- **Follow "The Django Way"**: Use Django's native tools (ORM, Forms, Class/Function-Based Views, Templates, Signals) before third-party libraries
- **Strict Minimalism**: Generate only requested code, avoid "gold plating" with unnecessary features
- **Performance**: Always use `select_related` and `prefetch_related` to avoid N+1 queries
- **Security**: Use `python-decouple` for environment variables, never hardcode secrets
- **Forms**: Always include `{% csrf_token %}` in POST forms and use Django Forms for validation
- **Testing**: Use `pytest` with `pytest-django` framework
- **Constants**: All global constants in `constants/constant.py` using `UPPER_SNAKE_CASE`

### TailwindCSS Rules
- **Utility-First Approach**: Use Tailwind utility classes directly in HTML
- **No Inline Styles**: Strictly prohibited to use `style="..."` attribute
- **Mobile-First Design**: Design for small screens first, use responsive classes (`sm:`, `md:`, `lg:`)
- **Component Classes**: Use `@apply` in `tailwind/base.css` for repeated utility patterns
- **Form Styling**: Define Tailwind classes as constants in `constants/form_styles.py`
- **Build Process**: Source in `tailwind/` directory, output to `static/css/styles.css`

### Template and Frontend Rules
- **No Logic in Templates**: Business logic belongs in views, not templates
- **No Inline Styles**: Use only Tailwind classes for styling
- **No HTML5 Validation**: Use server-side validation with Django Forms
- **Modular Components**: Use `{% include %}` for reusable components in `templates/partials/`
- **JavaScript**: Prefer vanilla JavaScript, use Alpine.js for simple interactions
- **Accessibility**: Use semantic HTML tags and ARIA attributes
- **Assets**: Serve Font Awesome and Alpine.js locally from `static/`