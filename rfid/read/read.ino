#include <SPI.h>
#include <MFRC522.h>

#define SDA_PIN 21
#define SCK_PIN 22
#define MOSI_PIN 23
#define MISO_PIN 19
#define RST_PIN 4

MFRC522 mfrc522(SDA_PIN, RST_PIN);
MFRC522::StatusCode status;
MFRC522::MIFARE_Key key;
byte block = 1;
byte len;
byte buffer[34];

void setup() {
  Serial.begin(9600);  // Initialize serial communications with the PC
  SPI.begin(SCK_PIN, MISO_PIN, MOSI_PIN, SDA_PIN);
  SPI.begin();         // Init SPI bus
  mfrc522.PCD_Init();  // Init MFRC522 card
  Serial.println(F("RFID reader ready. Present a card..."));
}

void loop() {
  // Reset the key for each new card
  for (byte i = 0; i < 6; i++) {
    mfrc522.PICC_HaltA();  // Make sure to halt any previous card session
    key.keyByte[i] = 0xFF;
  }
  
  // Wait until a new card is present and read its UID.
  if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial())
    return;

  // Authenticate and read the data from block 1
  Readinfo();

  // Halt communication with the card
  mfrc522.PICC_HaltA();
  mfrc522.PCD_StopCrypto1();
}

void Readinfo() {
  len = 18;
  status = mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, block, &key, &(mfrc522.uid));
  if (status != MFRC522::STATUS_OK) {
    Serial.print(F("Authentication failed: "));
    Serial.println(mfrc522.GetStatusCodeName(status));
    return;
  }

  status = mfrc522.MIFARE_Read(block, buffer, &len);
  if (status != MFRC522::STATUS_OK) {
    Serial.print(F("Reading failed: "));
    Serial.println(mfrc522.GetStatusCodeName(status));
    return;
  }

  // Convert the read bytes to a string (assuming text was written)
  String cardData = "";
  for (uint8_t i = 0; i < 16; i++) {
    // Append character if not a space (you can change logic if needed)
    cardData += char(buffer[i]);
  }
  cardData.trim();  // Remove any extra whitespace

  Serial.print(F("Card Data: "));
  Serial.println(cardData);

  // Check if the card's data equals "ambulance" (case insensitive)
  if (cardData.equalsIgnoreCase("ambulance")) {
    Serial.println("AMBULANCE_DETECTED");
  }
}