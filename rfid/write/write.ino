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
int Status =1;
byte block;
byte len;
byte buffer[34];
void setup() {
  Serial.begin(9600);        // Initialize serial communications with the PC
  SPI.begin(SCK_PIN, MISO_PIN, MOSI_PIN, SDA_PIN);
  SPI.begin();               // Init SPI bus
  mfrc522.PCD_Init();        // Init MFRC522 card
  Serial.println(F("Write personal data on a MIFARE PICC "));
}

void loop() {
Status=1;
 for (byte i = 0; i < 6; i++) key.keyByte[i] = 0xFF;
  if ( ! mfrc522.PICC_IsNewCardPresent() || ! mfrc522.PICC_ReadCardSerial() ) 
    return;

  Serial.print(F("Card UID:"));    //Dump UID
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " ");
    Serial.print(mfrc522.uid.uidByte[i], HEX);
  }
  Serial.print(F(" PICC type: "));   // Dump PICC type
  MFRC522::PICC_Type piccType = mfrc522.PICC_GetType(mfrc522.uid.sak);
  Serial.println(mfrc522.PICC_GetTypeName(piccType));

  
  Serial.setTimeout(20000L) ;     // wait until 20 seconds for input from serial
  Serial.println(F("Type Product Name, ending with #"));
  block = 1;
  Writedata(block);
  if (Status==0)
  return;
  
  Serial.println();
  Serial.setTimeout(0);
  Serial.println("Writing Completed");
  mfrc522.PICC_HaltA(); // Halt PICC
  mfrc522.PCD_StopCrypto1(); 
}


void Writedata(byte block)
{
     len = Serial.readBytesUntil('#', (char *) buffer, 30) ; // read family name from serial
  for (byte i = len; i < 30; i++) buffer[i] = ' ';     // pad with spaces

   status = mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, block, &key, &(mfrc522.uid));
  if (status != MFRC522::STATUS_OK) {
    Serial.print(F("PCD_Authenticate() failed: "));
    Serial.println(mfrc522.GetStatusCodeName(status));
    Serial.println("ERROR");
    Status=0;
    return ;
  }
 
  else 
  {
     Serial.println(F("PCD_Authenticate() success: "));
  }
 

  
  status = mfrc522.MIFARE_Write(block, buffer, 16);
  if (status != MFRC522::STATUS_OK) {
    Serial.print(F("MIFARE_Write() failed: "));
    Serial.println(mfrc522.GetStatusCodeName(status));
    Serial.println("ERROR");
    Status=0;
     return ;
    }
    
  else 
  {
    Status=1;
    Serial.println(F("MIFARE_Write() success: "));
  }

}