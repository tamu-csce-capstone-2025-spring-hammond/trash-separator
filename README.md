# Waste Classification Web App

This project is a React-based web application that allows users to:
- **Scan a waste item using a webcam** or **Upload a waste image** for classification
- **View the waste classification history of uploaded items**

Once an image is captured or uploaded, it redirects to the **Results Page**. Users can also navigate to the **Item History Page** to view past classifications.

## Features

- **Scan Using Camera**: Opens the webcam to capture an image.
- **Upload Image**: Allows users to upload an image from their device.
- **Item History**: Navigates to a page that will display historical classification data.
- **Results Page**: Displays the captured or uploaded image.

## Tech Stack
- **React**: A JavaScript library for building user interfaces.
- **React Router**: For routing between pages in the app.
- **react-webcam**: For accessing the webcam to capture images.
- **CSS**: For styling the app.

## Installation

To get started, clone this repository and install the dependencies.

1. **Clone the repository** to your local machine:
    ```bash
    git clone https://github.com/your-username/react-image-scanner.git
    ```

2. **Navigate to the project folder**:
    ```bash
    cd react-image-scanner
    ```

3. **Install dependencies**:
    ```bash
    npm install
    ```

4. **Start the development server**:
    ```bash
    npm start
    ```

## Usage

1. **Home Page**:
    - Click the **"Scan Using Camera"** button to open the webcam and capture an image.
    - Click the **"Upload Image"** button to select and upload an image from your device.
    - Click **"Item History"** to go to the classification history page.

2. **Results Page**:
    - The captured or uploaded image will be displayed on the results page.
    - A **"Back to Home"** button is available to navigate back to the homepage.

3. **Item History Page**:
    - Displays a placeholder message. This will be updated in the future to show a history of uploaded/captured images with classifications.
