extern x;
enum Boolean
{
	false,
	true
};

typedef struct{
	int a;
	double c;
}mytype;

void fff(){
	int asdf = 1;
}

int main(int argc, char *argv[]) {
	int a, c;
	double b;
	int i;
	char ch;
	long f = 122L;
	const unsigned short g = 1;
//	double b = 12.3E2;	
	printf("a + b = c\n");
	printf("%d\n", sizeof(int));
	
	b = 12.3E2;
	b = 12.3 + 345 - 1. * 0.9999;
	c = 345;
	
	if (1) {
		a = b;
	}else if(0){
		c = 1;
	}else {
		b = a *c;}
	
	for (i = 0; i < 10; i++) {
		a += c?1:2;
	}
	
	do {
		a >>= 1;
		if (a < 0) {
			break;
		}else {
			continue;
		}
	} while (1);
	
	while (a) {
		a--;
		getc_unlocked(a);
	}
	
	switch (ch) {
		case 'a':
		case 'b':
			 break;
		case 'c':
			putchar(ch);
		case 'd':
			goto AHA;
		default:
			break;
	}
	
AHA: 
	a = 1;
}