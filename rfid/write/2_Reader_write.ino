#include <SPI.h>
#include <MFRC522.h>

// First RFID reader pins (from your original code)
#define SDA_PIN_1 21
#define SCK_PIN 22
#define MOSI_PIN 23
#define MISO_PIN 19
#define RST_PIN_1 4

// Second RFID reader pins (using available GPIO pins)
#define SDA_PIN_2 5  // Common SS/SDA pin for second reader
#define RST_PIN_2 27 // Common RST pin for second reader

// Create two MFRC522 instances
MFRC522 mfrc522_1(SDA_PIN_1, RST_PIN_1);
MFRC522 mfrc522_2(SDA_PIN_2, RST_PIN_2);

MFRC522::StatusCode status;
MFRC522::MIFARE_Key key;
int Status = 1;
byte block = 1;
byte len;
byte buffer[34];

void setup() {
  Serial.begin(9600);        // Initialize serial communications with the PC
  
  // Initialize SPI bus with the pins from your read code
  SPI.begin(SCK_PIN, MISO_PIN, MOSI_PIN);
  
  // Initialize both RFID readers
  mfrc522_1.PCD_Init();
  mfrc522_2.PCD_Init();
  
  Serial.println(F("Write personal data on a MIFARE PICC - Dual Reader System"));
}

void loop() {
  Status = 1;
  for (byte i = 0; i < 6; i++) key.keyByte[i] = 0xFF;
  
  // Check Reader 1
  if (mfrc522_1.PICC_IsNewCardPresent() && mfrc522_1.PICC_ReadCardSerial()) {
    Serial.println(F("Card detected on Reader 1"));
    ProcessCard(&mfrc522_1, 1);
  }
  
  // Check Reader 2
  if (mfrc522_2.PICC_IsNewCardPresent() && mfrc522_2.PICC_ReadCardSerial()) {
    Serial.println(F("Card detected on Reader 2"));
    ProcessCard(&mfrc522_2, 2);
  }
  
  delay(50); // Small delay to prevent too rapid scanning
}

void ProcessCard(MFRC522 *mfrc522, int readerNum) {
  Serial.print(F("Card UID on Reader "));
  Serial.print(readerNum);
  Serial.print(F(": "));
  
  // Dump UID
  for (byte i = 0; i < mfrc522->uid.size; i++) {
    Serial.print(mfrc522->uid.uidByte[i] < 0x10 ? " 0" : " ");
    Serial.print(mfrc522->uid.uidByte[i], HEX);
  }
  
  Serial.print(F(" PICC type: "));
  MFRC522::PICC_Type piccType = mfrc522->PICC_GetType(mfrc522->uid.sak);
  Serial.println(mfrc522->PICC_GetTypeName(piccType));
  
  Serial.print(F("Type Product Name for Reader "));
  Serial.print(readerNum);
  Serial.println(F(", ending with #"));
  
  Serial.setTimeout(20000L); // wait until 20 seconds for input from serial
  
  Writedata(block, mfrc522);
  
  if (Status == 0)
    return;
  
  Serial.println();
  Serial.setTimeout(0);
  Serial.println("Writing Completed");
  
  mfrc522->PICC_HaltA(); // Halt PICC
  mfrc522->PCD_StopCrypto1();
}

void Writedata(byte block, MFRC522 *mfrc522) {
  len = Serial.readBytesUntil('#', (char *) buffer, 30); // read data from serial
  for (byte i = len; i < 30; i++) buffer[i] = ' ';     // pad with spaces

  status = mfrc522->PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, block, &key, &(mfrc522->uid));
  if (status != MFRC522::STATUS_OK) {
    Serial.print(F("PCD_Authenticate() failed: "));
    Serial.println(mfrc522->GetStatusCodeName(status));
    Serial.println("ERROR");
    Status = 0;
    return;
  }
  else {
    Serial.println(F("PCD_Authenticate() success"));
  }
  
  status = mfrc522->MIFARE_Write(block, buffer, 16);
  if (status != MFRC522::STATUS_OK) {
    Serial.print(F("MIFARE_Write() failed: "));
    Serial.println(mfrc522->GetStatusCodeName(status));
    Serial.println("ERROR");
    Status = 0;
    return;
  }
  else {
    Status = 1;
    Serial.println(F("MIFARE_Write() success"));
  }
}
