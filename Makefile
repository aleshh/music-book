.PHONY: book pdf epub cover-text word-count clean

book: pdf epub

pdf:
	@./scripts/build-book.sh pdf

epub:
	@./scripts/build-book.sh epub

cover-text:
	@./scripts/build-cover.sh --text-only

word-count:
	@python3 ./scripts/word-count.py

clean:
	@./scripts/build-book.sh clean
