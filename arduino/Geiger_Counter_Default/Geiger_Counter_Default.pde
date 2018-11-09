/* Geiger Counter Kit - Default Sketch (v4)                         bHogan 7/7/11
 * Counts events/min. and outputs CPM & ~uSv/hr to LCD display and also to serial port.
 * Sample period shortens with increase in counts. Bar graph on LCD 
 * One of 2 conversion ratios can be selected via jumper. ACCURACY NOT VERIFIED
 * v4 adds check for voltage at the uC to indicate a low battery voltage
 *
 * SETUP: (Any 2x16 Hitachi HD44780 compatible LCD)
 * +5V LCD Vdd pin 2             >>>     Gnd LCD Vss pin 1, and R/W pin 5
 * LCD RS pin 4 to D3            >>>     LCD Enable pin 6 to D4
 * LCD D4 pin 11 to D5           >>>     LCD D5 pin 12 to D6
 * LCD D6 pin 13 to D7           >>>     LCD D7 pin 14 to D8
 * LCD LEDA pin 15 to ~1K to +5  >>>     LCD LEDK pin 16 to GND
 * 10K pot: - ends to +5V and Gnd, wiper to LCD VO pin (pin 3)
 * *INT from Geiger circuit is connected to PIN 2 and triggered as FALLING.
 * PIN 9 - jumper to GND if secondary conversion ratio is desired
 *
 * This program is free software; you can redistribute it and/or modify it under the
 * terms of the GNU General Public License as published by the Free Software
 * Foundation; either version 2.1 of the License, or any later version.
 * This program is distributed in the hope that it will be useful, but WITHOUT ANY
 * WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
 * PARTICULAR PURPOSE.  See the GNU General Public License for more details.
 * 
 * THIS PROGRAM AND IT'S MEASUREMENTS IS NOT INTENDED TO GUIDE ACTIONS TO TAKE, OR NOT
 * TO TAKE REGARDING EXPOSURE TO RADIATION. ALWAYS FOLLOW THE INSTRUCTIONS GIVEN BY
 * THE CIVIL AUTHORITIES. DO NOT RELY ON THIS PROGRAM!
 */

#include <LiquidCrystal.h>              // HD44780 compatible LCDs work with this lib
#define LED_PIN          13             // for debug only - flashes 5X at startup
#define TUBE_SEL          9             // jumper to select alt conversion to uSv

// HOW MANY CPM =1 uSV? Two commonly used sets of ratios for the SBM-20 & LND712 are defined:
// libelium now uses: 175.43 for SBM-20 and 100.00 for LND712
// www.utsunomia.com/y.utsunomia/Kansan.html use: 150.51 for SBM-20 and 123.14 for LND712
#define PRI_RATIO        175.43         // no TUBE_SEL jumper - SET FOR SBM-20
#define SEC_RATIO        100.00         // TUBE_SEL jumper to GND - SET FOR LND712

// sample periods < 10 sec cause rounding errors (3 sec minimum))
// HG: increased sample period to 30s
#define LONG_PERIOD      30000          // mS sample & display below 100 CPM
#define SHORT_PERIOD     5000           // mS sample & display above 100 CPM
#define FULL_SCALE       1000           // max CPM for 8 bars & overflow warning
#define LOW_VCC          4200 //mV      // if Vcc < LOW_VCC give low voltage warning

// instantiate the library and pass pins for (RS, Enable, D4, D5, D6, D7)
LiquidCrystal lcd(3, 4, 5, 6, 7, 8);    // default layout for the Geiger board 

volatile boolean newEvent = false;      // true when new event was caught by ISR
boolean lowVcc = false;                 // true when Vcc < LOW_VCC
unsigned long startTime, startPeriod, samplePeriod;
unsigned long currCnt, CPM;
unsigned long checkVccTime;
float uSv = 0.0;                        // CPM converted to VERY APPROXIMATE uSv
float uSvRate;                          // holds the rate selected by jumper
int Vcc_mV;                             // mV of Vcc from last check 

//Custom characters used for bar graph
byte bar_0[8] = {0x00, 0x00, 0x10, 0x10, 0x10, 0x00, 0x00, 0x00}; //blank
byte bar_1[8] = {0x10, 0x10, 0x18, 0x18, 0x18, 0x10, 0x10, 0x00}; //1 bar
byte bar_2[8] = {0x18, 0x18, 0x1c, 0x1c, 0x1c, 0x18, 0x18, 0x00}; //2 bars
byte bar_3[8] = {0x1C, 0x1C, 0x1e, 0x1e, 0x1e, 0x1C, 0x1C, 0x00}; //3 bars
byte bar_4[8] = {0x1E, 0x1E, 0x1f, 0x1f, 0x1f, 0x1E, 0x1E, 0x00}; //4 bars
byte bar_5[8] = {0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x00}; //5 bars
byte bar_6[8] = {0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x1F, 0x00}; //6 bars (same)

void setup(){
  Serial.begin(9600);                   // comspec 96,N,8,1
  attachInterrupt(0,GetEvent,FALLING);  // Geiger event on pin 2 triggers interrupt
  pinMode(LED_PIN,OUTPUT);              // setup LED pin
  pinMode(TUBE_SEL,INPUT);              // setup tube select jumper pin
  digitalWrite(TUBE_SEL, HIGH);         // set 20K pullup on jumper pin(low active)
  samplePeriod = LONG_PERIOD;           // start with long period
  Blink(LED_PIN,5);                     // show it's alive
  lcd.begin(16,2);                      // cols, rows of display (8x2, 16x2, etc.)
  lcd.createChar(0, bar_0);             // load 7 custom characters in the LCD
  lcd.createChar(1, bar_1);
  lcd.createChar(2, bar_2);
  lcd.createChar(3, bar_3);
  lcd.createChar(4, bar_4);
  lcd.createChar(5, bar_5);
  lcd.createChar(6, bar_6);
  lcd.setCursor(0,0);

  lcd.clear();                          // clear the screen
  lcd.print("   GEIGER KIT");           // display a simple banner
  delay (2000);                         // leave the banner up 2 sec.
  lcd.clear();                          // clear the screen
  if(digitalRead(TUBE_SEL)){            // read jumper to select conversion ratio
    uSvRate = PRI_RATIO;                // use the primary ratio defined
  }
  else{                                 // jumper is set to GND . . .
    uSvRate = SEC_RATIO;                // use the secondary ratio defined
  }
  lcd.print(uSvRate,0);                 // display conversion ratio in use 
  lcd.print(" CPM to uSv");
  lcd.setCursor(0,1);                   // set cursor on line 2
  Vcc_mV = readVcc();                   // read Vcc voltage
  lcd.print("Running at ");              // display it
  lcd.print(Vcc_mV/1000);
  lcd.print(".");
  lcd.print(Vcc_mV/100 % 10);
  lcd.print("V");
  delay (5000);                         // leave info up for 5 sec.
  lcd.clear();                          // clear the screen

  lcd.print("CPM ");                    // display static "CPM"
  lcd.setCursor(0,1);
  lcd.print("uSv/hr ");                 // display static "uSv/hr"
  startTime = millis();                 // start timing
  startPeriod = startTime;
  checkVccTime = startTime;
}


void loop(){
  if (millis() > checkVccTime + 2000){  // timer for check battery
    checkVccTime = millis();            // reset timer
    Vcc_mV = readVcc();
    if (Vcc_mV <= LOW_VCC) lowVcc = true; // check if Vcc is low 
    else lowVcc = false;
  }
  if (millis() > startPeriod + samplePeriod) ProcCounts(); // period is over
  if (newEvent){                        // add to current count
    currCnt++;
    newEvent = false;
  }
  //uncomment for self check (1/166ms X 60 = 360 CPM ~2 uSv on SBM-20)
  //newEvent = true;                      // simulate an interrupt
  //delay(166);                           // 166 mS ~= 6 Hz    
}


void ProcCounts(){ // aggregate totals and reset counters for each period
  CPM = (currCnt * 60) /(samplePeriod / 1000); // calc CPM for the period
  uSv = CPM / uSvRate;                         // make uSV conversion
  currCnt = 0;
  startPeriod = millis();                   // reset time
  if (CPM > 99)samplePeriod = SHORT_PERIOD; // shorten sample period if CPM > 100  
  else samplePeriod = LONG_PERIOD;  
  displayCount();
}


void displayCount(){
  lcd.setCursor(4, 0);                  // set cursor after "CPM "
  lcd.print("     ");                   // clear area
  lcd.setCursor(4, 0);                  // set cursor after "CPM" again
  lcd.print(CPM);                       // display CPM on line 1
  lcd.setCursor(7, 1);                  // as above for line 2
  lcd.print("          ");
  lcd.setCursor(7, 1);
  lcd.print(uSv,4);                     // display uSv/hr on line 2
  lcd.setCursor(9,0);                   // move cursor to 9th col, 1st line for lcd bar

  if (CPM <= FULL_SCALE) lcdBar(CPM);   // display bargraph on line 2
  else {                                // put warning on line 2 if > full scale
    lcd.print("        ");
    lcd.setCursor(9,0);
    lcd.print(">");
    lcd.print(FULL_SCALE);
  }
  if (lowVcc) {                         // overwrite display with battery voltage
    lcd.print("        ");
    lcd.setCursor(9,0);
    lcd.print("Vcc=");
    lcd.print(Vcc_mV/1000);
    lcd.print(".");
    lcd.print(Vcc_mV/100 % 10);
  }
  Serial.print("CPM = ");               // output the same info to the serial port
  Serial.print(CPM,DEC);
  Serial.print(" / ");
  Serial.print("uSv/h = ");
  Serial.println(uSv,4);     
}


void lcdBar(int counts){  // displays CPM as bargraph on 2nd line
  // Adapted from DeFex http://www.arduino.cc/cgi-bin/yabb2/YaBB.pl?num=1264215873/0
  int scaler = FULL_SCALE / 47;         // 8 char=47 "bars", scaler = counts/bar
  int cntPerBar = (counts / scaler);    // amount of bars needed to display the count
  int fullBlock = (cntPerBar / 6);      // divide for full "blocks" of 6 bars 
  int prtlBlock = (cntPerBar % 6 );     // calc the remainder of bars
  for (int i=0; i<fullBlock; i++){
    lcd.print(5,BYTE);                  // print full blocks
  }
  lcd.print(prtlBlock,BYTE);            // print remaining bars with custom char
  for (int i=(fullBlock + 1); i<8; i++){
    lcd.print(" ");                     // blank spaces to clean up leftover
  }  
}


void Blink(byte led, byte times){ // just to flash the LED
  for (byte i=0; i< times; i++){
    digitalWrite(led,HIGH);
    delay (150);
    digitalWrite(led,LOW);
    delay (100);
  }
}


long readVcc() { // SecretVoltmeter from TinkerIt
  long result;
  // Read 1.1V reference against AVcc
  ADMUX = _BV(REFS0) | _BV(MUX3) | _BV(MUX2) | _BV(MUX1);
  delay(2); // Wait for Vref to settle
  ADCSRA |= _BV(ADSC); // Convert
  while (bit_is_set(ADCSRA,ADSC));
  result = ADCL;
  result |= ADCH<<8;
  result = 1126400L / result; // Back-calculate AVcc in mV
  return result;
}


void GetEvent(){   // ISR triggered for each new event (count)
  newEvent = true;
}


