#include <SPI.h>
#include <MFRC522.h>

// Shared SPI pins
#define SCK_PIN 18
#define MISO_PIN 19
#define MOSI_PIN 23

// Reader 1 pins
#define SDA_PIN_1 5
#define RST_PIN_1 22

// Reader 2 pins
#define SDA_PIN_2 4
#define RST_PIN_2 21

// Create two MFRC522 instances
MFRC522 mfrc522_1(SDA_PIN_1, RST_PIN_1);
MFRC522 mfrc522_2(SDA_PIN_2, RST_PIN_2);

MFRC522::StatusCode status;
MFRC522::MIFARE_Key key;
byte block = 1;
byte len;
byte buffer[34];

void setup() {
  Serial.begin(9600);
  while (!Serial);

  // Initialize SPI bus
  SPI.begin(SCK_PIN, MISO_PIN, MOSI_PIN);
  
  // Initialize both RFID readers
  mfrc522_1.PCD_Init();
  mfrc522_2.PCD_Init();

  // Check if readers are connected
  Serial.println(F("Testing readers connections:"));
  
  byte version1 = mfrc522_1.PCD_ReadRegister(MFRC522::VersionReg);
  Serial.print(F("Reader 1 firmware version: 0x"));
  Serial.println(version1, HEX);
  
  byte version2 = mfrc522_2.PCD_ReadRegister(MFRC522::VersionReg);
  Serial.print(F("Reader 2 firmware version: 0x"));
  Serial.println(version2, HEX);
  
  Serial.println(F("RFID readers ready. Present cards..."));
  
  // Prepare key - all keys are set to FFFFFFFFFFFFh (factory default)
  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }
}

void loop() {
  // Check Reader 1
  if (mfrc522_1.PICC_IsNewCardPresent() && mfrc522_1.PICC_ReadCardSerial()) {
    Serial.println(F("Card detected on Reader 1"));
    ReadInfo(&mfrc522_1, 1);
    mfrc522_1.PICC_HaltA();
    mfrc522_1.PCD_StopCrypto1();
  }
  
  // Check Reader 2
  if (mfrc522_2.PICC_IsNewCardPresent() && mfrc522_2.PICC_ReadCardSerial()) {
    Serial.println(F("Card detected on Reader 2"));
    ReadInfo(&mfrc522_2, 2);
    mfrc522_2.PICC_HaltA();
    mfrc522_2.PCD_StopCrypto1();
  }
  
  delay(50); // Small delay between reading attempts
}

void ReadInfo(MFRC522 *mfrc522, int readerNum) {
  len = 18;
  status = mfrc522->PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, block, &key, &(mfrc522->uid));
  if (status != MFRC522::STATUS_OK) {
    Serial.print(F("Reader "));
    Serial.print(readerNum);
    Serial.print(F(" - Authentication failed: "));
    Serial.println(mfrc522->GetStatusCodeName(status));
    return;
  }

  status = mfrc522->MIFARE_Read(block, buffer, &len);
  if (status != MFRC522::STATUS_OK) {
    Serial.print(F("Reader "));
    Serial.print(readerNum);
    Serial.print(F(" - Reading failed: "));
    Serial.println(mfrc522->GetStatusCodeName(status));
    return;
  }

  // Convert the read bytes to a string
  String cardData = "";
  for (uint8_t i = 0; i < 16; i++) {
    cardData += char(buffer[i]);
  }
  cardData.trim();  // Remove any extra whitespace

  Serial.print(F("Reader "));
  Serial.print(readerNum);
  Serial.print(F(" - Card Data: "));
  Serial.println(cardData);

  // Check special values for each reader
  if (cardData.equalsIgnoreCase("ambulance")) {
    Serial.print(F("Reader "));
    Serial.print(readerNum);
    Serial.println(F(" - AMBULANCE_DETECTED"));
  }
  if (cardData.equalsIgnoreCase("Nano")) {
    Serial.print(F("Reader "));
    Serial.print(readerNum);
    Serial.println(F(" - NANO_GOATED"));
  }
}