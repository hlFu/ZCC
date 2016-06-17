	.file	"a.c"
	.intel_syntax noprefix
	.section	.rodata
.LC0:
	.string	"hello"
.LC1:
	.string	"%d\n"
	.text
	.globl	foo
	.type	foo, @function
foo:
	push	ebp
	mov	ebp, esp
	sub	esp, 8
	sub	esp, 12
	push	OFFSET FLAT:.LC0
	call	puts
	add	esp, 16
	sub	esp, 8
	push	DWORD PTR [ebp+8]
	push	OFFSET FLAT:.LC1
	call	printf
	add	esp, 16
	mov	eax, DWORD PTR [ebp+8]
	leave
	ret
	.size	foo, .-foo
	.globl	main
	.type	main, @function
main:
	lea	ecx, [esp+4]
	and	esp, -16
	push	DWORD PTR [ecx-4]
	push	ebp
	mov	ebp, esp
	push	ecx
	sub	esp, 20
	mov	DWORD PTR [ebp-12], 2
	sub	esp, 12
	push	DWORD PTR [ebp-12]
	call	foo
	add	esp, 16
	mov	DWORD PTR [ebp-16], eax
	sub	esp, 8
	push	DWORD PTR [ebp-16]
	push	OFFSET FLAT:.LC1
	call	printf
	add	esp, 16
	mov	eax, 0
	mov	ecx, DWORD PTR [ebp-4]
	leave
	lea	esp, [ecx-4]
	ret
	.size	main, .-main
	.ident	"GCC: (GNU) 5.3.1 20160406 (Red Hat 5.3.1-6)"
	.section	.note.GNU-stack,"",@progbits
