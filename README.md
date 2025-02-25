# Travel_Companion

Travel_Companion is a full-featured travel planning and itinerary management application designed to simplify your travel experience. Whether you’re planning a vacation, a business trip, or a family reunion, Travel_Companion provides a one-stop solution to organize your journey—from booking and scheduling to weather updates and attraction searches.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture & Design](#architecture--design)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
  - [Frontend](#frontend)
  - [Backend](#backend)
- [Installation & Setup](#installation--setup)
  - [Frontend Setup](#frontend-setup)
  - [Backend Setup](#backend-setup)
- [API Documentation](#api-documentation)
- [Authentication & Security](#authentication--security)
- [Usage & Workflow](#usage--workflow)
- [Troubleshooting & FAQs](#troubleshooting--faqs)
- [Contributing](#contributing)
- [Future Enhancements](#future-enhancements)
- [License](#license)

---

## Overview

Travel_Companion aims to deliver an intuitive and seamless travel planning experience. It combines itinerary creation, attraction search, calendar scheduling, and weather forecasting into one cohesive platform. The app is split into a responsive Vue.js-based frontend and a robust Django REST Framework backend that communicates with several external APIs to enrich user data.

---

## Features

### User Authentication
- **Secure registration and login.**
- **JWT token management with automatic refresh.**

### Itinerary Management
- **Multi-step itinerary creation process.**
- **Edit, review, and submit itineraries.**
- **Save detailed planning information, including day-to-day activities.**

### Attraction Search & Management
- **Advanced search functionality for attractions and local activities.**
- **Integration with Overpass API to retrieve points of interest.**
- **Translation of attraction names using Google Translate API for non-English entries.**

### Calendar & Drag-and-Drop Scheduling
- **Interactive calendar view for visualizing scheduled events.**
- **Drag-and-drop interface for planning daily activities.**

### Weather Forecasting
- **Real-time weather and forecast data retrieval using Open-Meteo API.**
- **Detailed weather views including temperature, wind, humidity, UV index, and sunrise/sunset times.**

### Responsive and Accessible UI
- **Fully responsive design for desktop and mobile.**
- **Accessibility considerations in UI design and navigation.**

### Performance & Concurrency
- **Asynchronous API calls using aiohttp for high-concurrency attraction searches.**
- **In-memory caching for translation to reduce API calls and improve responsiveness.**

---

## Architecture & Design

Travel_Companion’s architecture is designed around modularity and scalability:

### Separation of Concerns
- **Frontend:** Manages UI/UX using Vue.js.
- **Backend:** Handles data management, business logic, and API interactions using Django.

### API-Centric Design
- **RESTful endpoints** expose itinerary operations, weather data retrieval, and attraction searches, enabling easy integration with other platforms or mobile apps.

### Third-Party Integrations
- **Nominatim & Overpass APIs:** For geolocation and retrieving local attractions.
- **Open-Meteo API:** Provides weather forecasts.
- **Google Translate API (experimental):** Translates non-English attraction names.

### Token Management
- **JWT-based authentication** with secure token refresh to ensure a seamless user experience.

### Async Operations
- The backend leverages **asynchronous HTTP requests** to improve performance when dealing with external API calls.

---

## Tech Stack

### Frontend
- **Framework:** Vue.js 3
- **Routing:** Vue Router
- **State Management:** Pinia
- **UI Components:** Vue3 Form Wizard, SweetAlert2
- **HTTP Client:** Axios

### Backend
- **Framework:** Django with Django REST Framework
- **Authentication:** SimpleJWT for JWT token handling
- **Database:** MySQL
- **HTTP Clients:** Requests and aiohttp for synchronous and asynchronous calls

### External APIs
- **APIs:** Open-Meteo, Nominatim, Overpass API, Google Translate

### Other
- **Styling:** Tailwind CSS, CSS with media queries for responsive design
- **Caching:** In-memory caching for translation results

---

## Project Structure

## Frontend

The frontend is built with Vue.js and is organized for clarity and modularity. It features a clear separation of global files, components, views, utilities, and state management using Pinia.

### Entry Point & Global Files

- **main.ts**  
  Initializes the Vue application, sets up Pinia for state management, configures Vue Router for navigation, and loads any necessary tokens.

- **App.vue**  
  The root component that holds the main layout and router view.

- **main.css**  
  Contains global CSS rules for styling and responsive design (including Tailwind CSS for utility-first styling).

### Components & Views

#### LoginRegister.vue

A unified component that manages user authentication by toggling between login and registration modes.

- **Purpose:**  
  Replaces separate login, register, and home pages to provide a seamless authentication experience.

- **Features & Functionality:**
  - **Dynamic Form Panel:**  
    Displays a "Welcome Back" greeting in login mode and a "Create an Account" prompt in registration mode.
  - **Form Fields & Validation:**  
    Includes fields for username, email (registration mode only), and password. Validates inputs and displays error messages for incorrect or missing data.
  - **API Integration:**  
    On submission, performs an HTTP POST request to the backend endpoints (`users/login/` for login and `users/register/` for registration) using Axios.
  - **Loading State & Feedback:**  
    Shows a loading spinner during API calls and provides feedback via SweetAlert2 for success messages. On successful login, tokens are set in the auth store and the user is redirected to the calendar page.
  - **Mode Toggle:**  
    Allows users to switch between login and registration modes, resetting fields and errors as needed.

#### Calendar & Sidebar Components

Provides an interactive interface for managing travel itineraries and events.

- **Sidebar:**
  - **Toggleable Panel:**  
    Expand or collapse the sidebar to display controls and itinerary summaries.
  - **Search Functionality:**  
    Allows users to filter itineraries by title.
  - **Action Buttons:**  
    Buttons for creating itineraries and checking weather forecasts.
  - **Itinerary Summaries:**  
    Displays a list of itinerary summaries with options for editing or deleting, and clicking a title jumps the calendar view to the itinerary’s start date.
  - **Footer:**  
    Displays the current username and a logout button.

- **Calendar Display & Interaction:**
  - **Vue-Cal Integration:**  
    Uses Vue-Cal to render various calendar views (month, week, agenda) with drag-and-drop support for events.
  - **Event Management:**  
    Supports event creation, immediate addition to the calendar, and detailed event modals with SweetAlert2.
  - **Time Customization:**  
    Configured for a time-based view (8 AM to 6 PM) in a 12-hour format with custom time formatting.
  - **Data Handling & Persistence:**  
    Events and itineraries are saved to and retrieved from local storage, ensuring data persists between sessions.
  - **Backend Communication:**  
    Deleting an itinerary triggers an API call (using Axios) to remove it from both the local interface and the MySQL database.

#### ItineraryForm.vue

A guided, multi-step form for creating or updating a travel itinerary.

- **Overview:**  
  Utilizes a form wizard divided into four sequential steps, each with its own validation and state management.
  
- **Structure & Navigation:**
  - **Close Button:**  
    Allows users to exit the form at any time.
  - **Form Wizard:**  
    Encapsulates the main content, with “Next” and “Back” buttons fixed at the bottom of the viewport for easy navigation.
  
- **Step-by-Step Breakdown:**
  - **Step 1 – Itinerary Information:**  
    Collects basic details such as title, city, state, country, start/end dates, and travel reason. An “Other” option reveals an additional input.
  - **Step 2 – Attractions:**  
    Enables selection of attractions. Validation ensures at least one attraction is added.
  - **Step 3 – Plan Activities:**  
    Provides a drag-and-drop interface for scheduling attractions into a daily timeline with automated conflict detection.
  - **Step 4 – Review & Submit:**  
    Summarizes the itinerary details and planned activities. On submission, data is saved to local storage and an API call is made (POST for creation, PUT for updates). The form resets for subsequent uses.
  
- **Data Management & Validation:**  
  - Uses shared state via Vue’s provide/inject mechanism to ensure real-time data updates.
  - Pre-populates data from local storage in edit mode, then clears stale data.
  - Validates each step before allowing navigation to the next step.

#### WeatherUI.vue

An integrated weather interface for checking current conditions, forecasts, and managing favorite cities.

- **Overall Layout & Navigation:**
  - **Sidebar Navigation:**  
    Includes icons for City Weather, Favorite Cities, and Trip Weather. Hover tooltips and an exit button allow quick navigation back to the calendar.
  - **Main Content Area:**  
    Dynamically displays different views based on user selection.

- **City Weather View:**
  - **Search Interface:**  
    Provides fields for entering city and country, with automatic capitalization and a loading spinner during API calls.
  - **Current Weather Display:**  
    Shows location, current date/time (adjusted via Luxon), temperature with dynamic icons, wind speed, humidity, UV index, and sunrise/sunset times.
  - **Forecast Sections:**  
    - **Hourly Forecast:**  
      Displays the next 25 hours in a scrollable horizontal row.
    - **10-Day Forecast:**  
      Provides daily high/low temperatures with concise day labels.

- **Favorites View:**
  - Allows searching and managing saved favorite cities, displaying key weather details for each.
  - Interaction includes loading a favorite city’s weather data or removing it from the list.

- **Trip Weather View:**
  - Retrieves weather data for upcoming travel events (within the next week), with navigation for different event dates.
  - Displays detailed event-based weather summaries.

- **Performance Optimization & Data Management:**
  - Caches trip weather data in local storage to reduce redundant API calls.
  - Dynamically updates the current time and weather information based on user interactions.

### Utilities & Stores

- **API Module (api.ts):**  
  Configures Axios with token refresh interceptors for secure backend communication.

- **Authentication Store (auth.ts):**  
  Manages authentication state, token persistence, and token expiration logic using Pinia.

---

## Backend

The backend is built with Django and Django REST Framework, structured to handle core application logic, user management, and external API integrations.

### Key Modules & Files

#### Views & Endpoints

- **ItineraryViewSet (main/views.py):**  
  Exposes endpoints for CRUD operations on itineraries, as well as endpoints for fetching weather data (`/weather/`), searching attractions (`/attractions/`), and finding nearby cities (`/nearby-cities/`).

- **User Management (users/views.py):**  
  Handles user registration and profile management.

#### Models & Serializers

- **Itinerary Model (main/models.py):**  
  Represents travel itineraries with fields for title, destination, dates, reason, and JSON-based planning details.

- **ItinerarySerializer (main/serializers.py):**  
  Serializes and validates itinerary data.

- **User & Profile Serializers (users/serializers.py):**  
  Manage user data serialization and registration workflows.

#### External API Integration & Concurrency

- Utilizes both synchronous (requests) and asynchronous (aiohttp) HTTP calls to communicate with external APIs (e.g., Nominatim, Overpass, Open-Meteo).
- Implements in-memory caching for translation results to improve performance.

#### Settings & Configuration

- Configured for CORS to enable secure communication between the frontend and backend.
- Uses environment variables to manage sensitive data and database credentials.
- JWT settings in `travelcompanion/settings.py` handle token expiration and refresh for secure user authentication.

---

## Project Directory Structure

```plaintext
├── frontend
│   ├── src
│   │   ├── assets
│   │   ├── components
│   │   │   ├── CalendarView.vue
│   │   │   ├── ItineraryForm
│   │   │   │   ├── Step1_ItineraryInfo.vue
│   │   │   │   ├── Step2_Activities.vue
│   │   │   │   ├── Step3_PlanActivities.vue
│   │   │   │   └── Step4_Review.vue
│   │   │   ├── LoginRegister.vue
│   │   │   └── WeatherUI.vue
│   │   ├── router
│   │   │   └── index.ts
│   │   ├── stores
│   │   │   └── auth.ts
│   │   ├── App.vue
│   │   └── main.ts
│   ├── tailwind.config.js
│   └── package.json
│
├── backend
│   ├── main
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── admin.py
│   ├── users
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── admin.py
│   ├── travelcompanion
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── manage.py

```
---
# Installation & Setup

## Frontend Setup

### Clone the Repository:
git clone https://github.com/yourusername/Travel_Companion.git  
cd Travel_Companion/frontend

### Install Dependencies:
npm install

### Run the Development Server:
npm run dev  
The app will typically run at http://localhost:5173.

### Configuration:
Ensure that the API base URL in api.ts matches your backend URL (e.g., http://localhost:8000/api/).

## Backend Setup

### Clone the Repository:
git clone https://github.com/yourusername/Travel_Companion.git  
cd Travel_Companion/backend

### Set Up Virtual Environment & Install Requirements:
python -m venv venv  
source venv/bin/activate   # On Windows use: venv\Scripts\activate  
pip install -r requirements.txt

### Database Setup:
Configure your MySQL credentials in a .env file. Ensure that your MySQL server is running and the specified database exists.

### Run Migrations:
python manage.py migrate

### Create Superuser (Optional):
python manage.py createsuperuser

### Run the Server:
python manage.py runserver  
The API will be available at http://localhost:8000.

# API Documentation

## Itinerary Endpoints

### List Itineraries:
- **GET /api/itineraries/**  
  Retrieves all itineraries for the authenticated user.

### Create Itinerary:
- **POST /api/itineraries/**  
  Payload includes title, destination details, start/end dates, reason, and planning details.

### Update Itinerary:
- **PUT /api/itineraries/<id>/**  
  Update an existing itinerary. Requires the itinerary ID.

### Delete Itinerary:
- **DELETE /api/itineraries/<id>/**  
  Deletes the specified itinerary.

## Weather Data

### Fetch Weather:
- **GET /api/itineraries/weather/?city=<city_name>**  
  Retrieves current and forecast weather for the specified city.

## Attraction Search

### Search Attractions:
- **GET /api/itineraries/attractions/**  
  Query parameters include city, state, country, and optional filters for category and keyword.

## Nearby Cities

### Get Nearby Cities:
- **GET /api/itineraries/nearby-cities/?city=<city_name>&radius=<miles>**  
  Returns cities within the given radius based on the input city’s coordinates.

## Authentication & Security

Travel_Companion uses JWT for stateless authentication:

- **Token Storage:**  
  Tokens are stored in both Pinia (state management) and localStorage.

- **Auto-Refresh:**  
  Axios interceptors check token expiration and automatically refresh tokens before they expire.

- **Backend Security:**  
  Endpoints require authentication (except for public routes) and leverage Django REST Framework’s permission classes.

# Usage & Workflow

## User Onboarding:
- **Registration:**  
  New users can register using the sign-up form.
- **Login:**  
  Existing users log in to access personalized itinerary data.

## Itinerary Creation:
1. **Step 1:**  
   Input basic travel information (title, destination, dates, reason).
2. **Step 2:**  
   Search for and add attractions/activities. Advanced filters help you refine your search.
3. **Step 3:**  
   Plan day-to-day activities using an interactive calendar and drag-and-drop scheduling.
4. **Step 4:**  
   Review your itinerary in a timeline view before final submission.

## Calendar & Weather:
- **Calendar:**  
  Visualize your trip events in an interactive calendar. Edit events by dragging them or clicking for details.
- **Weather:**  
  Check detailed weather forecasts for your trip dates. Use the weather module to add cities to your favorites.

## Managing Itineraries:
- View, edit, or delete itineraries through the calendar interface.
- All updates automatically sync with the backend via secure API calls.

# Troubleshooting & FAQs

- **Q: I’m having trouble logging in. What should I do?**  
  A: Ensure that you have registered an account. Check your network connectivity and verify that the backend server is running. If the issue persists, clear localStorage and try again.

- **Q: My itinerary isn’t saving.**  
  A: Verify that all required fields are filled out correctly. Check the browser console for errors related to token expiration or network issues.

- **Q: Weather data is not displaying.**  
  A: Confirm that you are connected to the internet and that the backend can reach the Open-Meteo API. Also, check the city name format.

- **Q: How do I update my account information?**  
  A: Currently, account details are managed through the registration process. Future updates may include a dedicated profile management page.

# Contributing

We welcome contributions to improve Travel_Companion! To contribute:

### Fork the Repository:
- Create your own fork on GitHub.

### Create a Feature Branch:
- Develop your feature or fix on a new branch:  
  `git checkout -b feature/my-new-feature`

### Commit Changes:
- Follow best practices and write clear commit messages.

### Open a Pull Request:
- Submit a pull request detailing your changes and the problem it solves.

### Code Reviews:
- Your pull request will be reviewed and feedback provided before merging.

# Future Enhancements

- **Mobile Application:**  
  Develop a native mobile app for iOS and Android for offline planning and notifications.
- **Social Sharing:**  
  Allow users to share itineraries and travel plans on social media.
- **Enhanced Analytics:**  
  Integrate data analytics to provide insights about popular attractions and travel trends.
- **User Profile Management:**  
  Expand user account functionality with profile updates and trip history.
- **Improved Localization:**  
  Support multiple languages and localizations for a broader global audience.

---
