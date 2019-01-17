#include "bcm2835.h"
#include "Utilities.h"

void main()
{
bcm2835_init();
pinModeOutput(LED_PIN);

while (1)
 {
	 digitalWrite(LED_PIN, HIGH);
	 delay_ms(3000);
	 digitalWrite(LED_PIN, LOW);
	 delay_ms(3000);
 }
}
