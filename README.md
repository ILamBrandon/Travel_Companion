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
- **Styling:** CSS with media queries for responsive design
- **Caching:** In-memory caching for translation results

---

## Project Structure

### Frontend

#### Entry Point & Global Files
- **`main.ts`:** Initializes the Vue application, sets up Pinia and Vue Router, and loads tokens.
- **`app.vue`:** Root component that contains the main layout and router view.
- **`main.css`:** Global CSS for styling and responsive design.

#### Components & Views
- **Home Page (`home.vue`):**  
  The welcome page that introduces the app features.
- **Authentication (`login.vue` & `register.vue`):**  
  Forms and UI for user login and account creation.
- **Calendar (`CalendarView.vue`):**  
  Interactive calendar with event scheduling, drag-and-drop functionality, and sidebar navigation.
- **Itinerary Form (`ItineraryForm.vue` and steps `step_1.vue`, `step2.vue`, `step3.vue`, `step4.vue`):**  
  A guided multi-step process to collect itinerary information, attractions, planning details, and final review.
- **Weather Interface (`WeatherUI.vue`):**  
  Provides search functionality for weather data and displays detailed forecast information.

#### Utilities & Stores
- **API Module (`api.ts`):**  
  Configures Axios with token refresh interceptors for secure API communication.
- **Authentication Store (`auth.ts`):**  
  Manages authentication state, token persistence, and expiration logic.

### Backend

#### Views & Endpoints
- **ItineraryViewSet (`main/views.py`):**  
  Exposes endpoints for CRUD operations, weather data (`/weather/`), attraction searches (`/attractions/`), and nearby cities (`/nearby-cities/`).
- **User Management (`users/views.py`):**  
  Handles user registration and profile management.

#### Models & Serializers
- **Itinerary Model (`main/models.py`):**  
  Represents a travel itinerary with fields for title, destination, dates, reason, and JSON-based planning details.
- **ItinerarySerializer (`main/serializer.py`):**  
  Serializes and validates itinerary data.
- **User & Profile Serializers (`users/serializer.py`):**  
  Manage user data and registration workflows.

#### External API Integration & Concurrency
- Utilizes both synchronous (`requests`) and asynchronous (`aiohttp`) HTTP calls to communicate with external APIs such as Nominatim, Overpass, and Open-Meteo.
- Implements in-memory caching for translations to improve performance.

#### Settings & Configuration
- **CORS:** Configured to allow the frontend to communicate with the backend.
- **Environment Variables:** Used for sensitive data and database credentials.
- **JWT Settings:** Configured in `travelcompanion/settings.py` for token expiration and refresh.

---

## Installation & Setup

### Frontend Setup

1. **Clone the Repository:**