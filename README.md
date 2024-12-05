# MedBlock: Blockchain-based Medicine Tracking System

![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Project Overview

MedBlock is a blockchain-based application system designed to detect and prevent counterfeit medicines in the pharmaceutical supply chain. By utilizing blockchain technology, MedBlock ensures the authenticity of medicines and guarantees their safe journey from manufacturer to patient. The system creates an immutable and transparent record of medication movement, providing visibility and verification to all stakeholders in the pharmaceutical ecosystem.

This is a project i have completed during my college days.

### Key Features

- **Blockchain-based Tracking**: Medication movement is recorded on a blockchain, ensuring tamper-proof and transparent tracking.
- **Unique Identifier**: Each medication package is assigned a unique identifier, linked to its blockchain record.
- **Authentication**: Stakeholders (manufacturer, distributor, retailer, and customer) can verify medication authenticity via a secure interface.
- **QR Code Generation**: Each product will have a QR code generated for authenticity verification.
- **Secure Data Storage**: All transactions are recorded on a private blockchain network.
- **Billings Dashboard for Retailers**: Retailers have access to a billing dashboard to track sales and generate invoices.

### Benefits

- **Counterfeit Prevention**: Prevents counterfeit medicines from entering the supply chain.
- **Patient Safety**: Ensures patients receive authentic and safe medicines.
- **Transparency**: Provides real-time visibility into the movement and ownership of medication.
- **Complete Product History**: Full transaction history of the product from manufacturer to patient, traceable through QR codes.

### Users

- **Manufacturer**: Can create and add products and units, generate unique identifiers, and register them on the blockchain.
- **Distributor**: Manages shipments, verifies the authenticity of received products, and sends products to retailers.
- **Retailer**: Marks received shipments, verifies the authenticity of the products, and sells to customers. Has access to a billing dashboard.
- **Customer**: Can verify product authenticity and view their purchase history.

## Installation

To run the MedBlock project locally, follow the steps below:

### Prerequisites

- Python 3.x
- Django 3.x or above
- Node.js (for managing any frontend dependencies)

### Steps to Install

1. **Clone the Repository**:

    ```bash
    git clone https://github.com/yourusername/medblock.git
    cd medblock
    ```

2. **Create a Virtual Environment**:

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use venv\Scripts\activate
    ```

3. **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Run Migrations**:

    ```bash
    python manage.py migrate
    ```

5. **Create a Superuser**:

    ```bash
    python manage.py createsuperuser
    ```

    Follow the prompts to create the superuser account for accessing the admin dashboard.

6. **Start the Development Server**:

    ```bash
    python manage.py runserver
    ```

7. Open a web browser and navigate to `http://127.0.0.1:8000` to start using the application.

## Libraries Used

- **Django**: Web framework used for building the backend of the application.
- **Pillow**: Python Imaging Library (PIL) used for handling image creation and manipulation, such as generating product QR codes.
- **ReportLab**: Used for generating PDF reports (e.g., invoices).
- **qrcode[pil]**: Library used for generating QR codes to verify product authenticity.

## Project Architecture

### Blockchain Integration

MedBlock uses blockchain technology to create an immutable and transparent record of each unit’s journey from manufacturer to customer. Each product or unit is assigned a unique identifier (UUID) that is linked to its blockchain record.

### QR Code for Authentication

Every product in the system has a unique QR code. The QR code can be scanned to verify the authenticity of the product by checking its blockchain record.

### Backend (Django)

- **Models**: The system consists of models such as `Product`, `Shipment`, `Bill`, `Unit`, and `Transaction` to track the flow of products.
- **Views**: Provides API and webpage views for managing products, verifying authenticity, creating shipments, and generating invoices.
- **Authentication**: Users are authenticated and authorized through Django’s built-in authentication system.

### Frontend

- **HTML/CSS**: Basic structure and styles for the application.
- **JavaScript**: Used for handling dynamic features like QR code scanning, unit selection based on products, and invoice generation.
- **Bootstrap**: Responsive frontend framework used to build the user interface.

## Use Cases

### Manufacturer

1. Add products and units.
2. Generate unique QR codes for each unit.
3. Track the movement of each unit on the blockchain.

### Distributor

1. Receive shipments and mark them as received.
2. Verify authenticity of the products via QR code scanning.
3. Send products to retailers.

### Retailer

1. Mark received shipments as confirmed.
2. Sell products to customers.
3. Verify product authenticity via QR codes.
4. Use the billing dashboard to generate invoices for sales.

### Customer

1. Verify product authenticity using the QR code.
2. View purchase history and transaction details.

## Technical Details

- **Blockchain Platform**: Uses a private blockchain network for secure and efficient tracking.
- **Smart Contracts**: Implements smart contracts for automated authentication and alert systems.
- **Data Storage**: Leverages secure and decentralized data storage solutions.

## Future Vision

MedBlock aims to empower a secure, transparent, and patient-centric pharmaceutical ecosystem. With blockchain, we aim to eradicate counterfeit medicines and guarantee the authenticity of each product, building trust in the pharmaceutical supply chain.

## Contributing

If you'd like to contribute to MedBlock, feel free to fork the repository and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

