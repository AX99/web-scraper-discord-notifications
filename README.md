# Amazon Flex Monitor

A Flask-based web scraping service that monitors Amazon Flex recruitment pages for availability and sends notifications via Discord. Designed to run on Google Cloud Run with automated scheduling.

## How It Works

The application performs the following:

1. **Web Scraping**: Uses Selenium WebDriver to navigate to the Amazon Flex recruitment page
2. **Text Detection**: Searches for specific text that indicates whether Amazon is accepting new delivery partners
3. **Discord Notifications**: Sends status updates to a Discord channel via webhooks
4. **HTTP API**: Exposes a POST endpoint that can be triggered manually or via scheduled jobs

### Key Features

- Headless Chrome browser automation
- Multiple CSS/XPath selector fallbacks for robust element detection
- Intelligent waiting for dynamic content to load
- Discord webhook integration with custom branding
- Environment-based configuration
- Health monitoring and error reporting

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Cloud Scheduler │───▶│   Cloud Run     │───▶│   Discord       │
│  (Cron Job)     │    │   (Flask App)   │    │   (Webhook)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Amazon Flex    │
                       │  Website        │
                       └─────────────────┘
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `WEBSITE_URL` | The Amazon Flex URL to monitor | Yes |
| `SEARCH_TEXT` | Text to search for on the page | Yes |
| `DISCORD_WEBHOOK_URL` | Discord webhook URL for notifications | Yes |
| `PORT` | Port for the Flask application | No (defaults to 8080) |

## Local Development

### Prerequisites

- Python 3.13+
- Chrome browser (for Selenium)
- Docker (for containerisation)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd amazon-flex
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

5. **Run locally**
   ```bash
   python main.py
   ```

6. **Test the endpoint**
   ```bash
   curl -X POST http://localhost:8080/
   ```

### Debugging in VS Code

Use the provided launch configuration:

1. Open VS Code in the project directory
2. Set breakpoints in your code
3. Press F5 and select "Python: Flask"
4. The debugger will attach to the Flask application

## Docker

### Building the Image

```bash
docker build -t amazon-flex-monitor .
```

### Running with Docker

```bash
docker run -p 8080:8080 \
  -e WEBSITE_URL="https://flex.amazon.co.uk/recruiting-cities" \
  -e SEARCH_TEXT="We are not looking for more delivery partners" \
  -e DISCORD_WEBHOOK_URL="your-discord-webhook-url" \
  amazon-flex-monitor
```

### Docker Compose

```yaml
version: '3.8'
services:
  amazon-flex-monitor:
    build: .
    ports:
      - "8080:8080"
    environment:
      - WEBSITE_URL=https://flex.amazon.co.uk/recruiting-cities
      - SEARCH_TEXT=We are not looking for more delivery partners
      - DISCORD_WEBHOOK_URL=your-discord-webhook-url
```

## Deployment to Google Cloud Run

### Prerequisites

- Google Cloud SDK installed and configured
- Docker configured for Google Cloud
- Billing enabled on your Google Cloud project

### Build and Push to Container Registry

```bash
# Configure Docker for GCP
gcloud auth configure-docker

# Build and tag the image
docker build -t gcr.io/[PROJECT-ID]/amazon-flex-monitor .

# Push to Container Registry
docker push gcr.io/[PROJECT-ID]/amazon-flex-monitor
```

### Deploy to Cloud Run

```bash
gcloud run deploy amazon-flex-monitor \
  --image gcr.io/[PROJECT-ID]/amazon-flex-monitor \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars WEBSITE_URL="https://flex.amazon.co.uk/recruiting-cities" \
  --set-env-vars SEARCH_TEXT="We are not looking for more delivery partners" \
  --set-env-vars DISCORD_WEBHOOK_URL="your-discord-webhook-url" \
  --memory 512Mi \
  --cpu 1 \
  --timeout 900
```

### Set up Automated Scheduling

Create a Cloud Scheduler job to trigger the service regularly:

```bash
gcloud scheduler jobs create http amazon-flex-check \
  --schedule="*/15 * * * *" \
  --uri=[CLOUD-RUN-SERVICE-URL] \
  --http-method=POST \
  --location=us-central1
```

## API Reference

### POST /

Triggers a website check and sends Discord notification.

**Response:**
- `200 OK`: Check completed successfully
- `400 Bad Request`: Missing required environment variables
- `500 Internal Server Error`: Error during execution

**Example Response:**
```
🔍 Text 'We are not looking for more delivery partners' not found in target element on https://flex.amazon.co.uk/recruiting-cities
```

## Monitoring and Logs

### View Cloud Run Logs

```bash
gcloud logs read --project=[PROJECT-ID] --filter="resource.type=cloud_run_revision"
```

### Check Service Status

```bash
gcloud run services describe amazon-flex-monitor --region=us-central1
```

## Troubleshooting

### Common Issues

1. **Element not found**: The website structure may have changed. Update the CSS selectors in the code.

2. **Timeout errors**: Increase the WebDriverWait timeout or add more explicit waits.

3. **Discord webhook not working**: Verify the webhook URL is correct and the channel exists.

4. **Chrome driver issues**: Ensure Chrome is installed in the container and WebDriver is up to date.

### Debug Locally

Run with verbose logging:
```bash
FLASK_DEBUG=1 python main.py
```

## Security Considerations

- Store sensitive environment variables in Google Secret Manager
- Use IAM roles with minimal required permissions
- Enable Cloud Run authentication if the service should not be public
- Regularly update dependencies for security patches

## Cost Optimisation

- Set appropriate CPU and memory limits
- Use Cloud Scheduler instead of keeping the service running continuously
- Set reasonable request timeouts
- Monitor usage with Cloud Monitoring

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license here] 