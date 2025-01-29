def add_to_google_sheet(purchase):
    # Authenticate with Google Sheets API
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = 'path/to/credentials.json'  # Replace with your credentials file

    credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=credentials)

    # Spreadsheet and range configuration
    SPREADSHEET_ID = 'your_spreadsheet_id'  # Replace with your spreadsheet ID
    RANGE = 'Sheet1!A1:E1'  # Replace with your desired sheet and range

    # Prepare data
    values = [[
        purchase.event_ticket.event.title,
        purchase.event_ticket.ticket_category.name,
        purchase.user_email,
        purchase.quantity,
        purchase.total_price,
    ]]
    body = {'values': values}

    # Append data to Google Sheet
    sheet = service.spreadsheets()
    sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE,
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body=body
    ).execute()
