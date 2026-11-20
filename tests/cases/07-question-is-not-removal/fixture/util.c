static int ready;

void legacy_init(void)
{
	ready = 1;
}

int main(void)
{
	legacy_init();
	return ready ? 0 : 1;
}
