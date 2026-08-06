.PHONY: book pdf epub clean

book: pdf epub

pdf:
	@./scripts/build-book.sh pdf

epub:
	@./scripts/build-book.sh epub

clean:
	@./scripts/build-book.sh clean
