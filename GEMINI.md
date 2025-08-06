# Gemini Preferences

This document outlines the development preferences and conventions for the SuiTune project, as specified by the user.

## Language Preference

- **Primary:** Chinese (中文)
- **Secondary:** English

## General Philosophy

- **Coding Style:** Adhere to the principles of "The Art of UNIX Programming," emphasizing simplicity, clarity, and stability.
- **Technology Choices:** Prioritize the latest, most popular, and stable versions of frameworks, libraries, and plugins.

## Technology Stack

- **Backend:** Django
- **Frontend:** Tailwind CSS V4
- **Core Django Plugins:**
    - `django-allauth` for authentication.
    - `djangorestframework` for building APIs.

## Project Conventions (from README.md)

- **Product Name:** SuiTune
- **Short Code:** sui
- **Environment Variable Prefix:** `SUITUNE_`
- **Database Table Prefix:** `sui_`
- **Nginx Internal Stream Path:** `/sui_stream/`
- **Static Asset Path:** `/static/suitune/`
- **Channels:** `music` | `talk` | `tv` | `ambient`
