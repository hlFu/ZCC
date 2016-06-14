	.file	"test4.c"
	.intel_syntax noprefix
	.comm	g_fast,4,4
	.local	s_g_fast
	.comm	s_g_fast,4,4
	.section	.rodata
.LC0:
	.string	"%d\n"
	.text
	.globl	main
	.type	main, @function
main:
	push	ebp
	mov	ebp, esp
	and	esp, -16
	sub	esp, 32
	mov	DWORD PTR [esp+28], 1
	mov	DWORD PTR s_l_fast.1829, 2
	mov	eax, DWORD PTR s_l_fast.1829
	add	DWORD PTR [esp+28], eax
	mov	eax, DWORD PTR s_l_fast.1829
	mov	DWORD PTR [esp], eax
	call	foo
	mov	DWORD PTR [esp+28], eax
	mov	eax, DWORD PTR [esp+28]
	mov	DWORD PTR [esp+4], eax
	mov	DWORD PTR [esp], OFFSET FLAT:.LC0
	call	printf
	mov	eax, 0
	leave
	ret
	.size	main, .-main
	.globl	foo
	.type	foo, @function
foo:
	push	ebp
	mov	ebp, esp
	mov	eax, DWORD PTR [ebp+8]
	add	eax, 1
	pop	ebp
	ret
	.size	foo, .-foo
	.local	s_l_fast.1829
	.comm	s_l_fast.1829,4,4
	.ident	"GCC: (Ubuntu 4.8.2-19ubuntu1) 4.8.2"
	.section	.note.GNU-stack,"",@progbits
