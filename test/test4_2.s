	.file	"test4_2.c"
	.intel_syntax noprefix
	.section	.rodata.str1.1,"aMS",@progbits,1
.LC0:
	.string	"%d\n"
	.text
	.globl	main
	.type	main, @function
main:
	push	ebp
	mov	ebp, esp
	and	esp, -16
	sub	esp, 16
	mov	DWORD PTR s_l_fast.2034, 2
	mov	DWORD PTR [esp+8], 3
	mov	DWORD PTR [esp+4], OFFSET FLAT:.LC0
	mov	DWORD PTR [esp], 1
	call	__printf_chk
	mov	eax, 0
	leave
	ret
	.size	main, .-main
	.globl	foo
	.type	foo, @function
foo:
	mov	eax, DWORD PTR [esp+4]
	add	eax, 1
	ret
	.size	foo, .-foo
	.local	s_l_fast.2034
	.comm	s_l_fast.2034,4,4
	.comm	g_fast,4,4
	.ident	"GCC: (Ubuntu 4.8.2-19ubuntu1) 4.8.2"
	.section	.note.GNU-stack,"",@progbits
