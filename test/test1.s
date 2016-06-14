	.file	"test1.c"
	.intel_syntax noprefix
	.comm	g_i,4,4
	.local	ss
	.comm	ss,4,4
	.local	sss
	.comm	sss,4,4
	.text
	.globl	main
	.type	main, @function
main:
	push	ebp
	mov	ebp, esp
	and	esp, -16
	sub	esp, 32
	add	DWORD PTR [esp+20], 1
	mov	DWORD PTR [esp+24], 1
	mov	eax, DWORD PTR [esp+20]
	add	DWORD PTR [esp+24], eax
	mov	eax, DWORD PTR [esp+24]
	mov	DWORD PTR [esp], eax
	call	foo
	mov	DWORD PTR [esp+28], eax
	nop
	leave
	ret
	.size	main, .-main
	.globl	foo
	.type	foo, @function
foo:
	push	ebp
	mov	ebp, esp
	sub	esp, 16
	mov	DWORD PTR [ebp-8], 2
	mov	DWORD PTR [ebp-4], 3
	add	DWORD PTR [ebp-8], 1
	mov	eax, DWORD PTR [ebp+8]
	add	eax, 1
	leave
	ret
	.size	foo, .-foo
	.ident	"GCC: (Ubuntu 4.8.2-19ubuntu1) 4.8.2"
	.section	.note.GNU-stack,"",@progbits
