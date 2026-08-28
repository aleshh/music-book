.PHONY: book pdf epub paperback paperback-cover cover-text word-count clean

book: pdf epub

pdf:
	@./scripts/build-book.sh pdf

epub:
	@./scripts/build-book.sh epub

paperback: pdf paperback-cover

paperback-cover:
	@./scripts/build-paperback-cover.sh

cover-text:
	@./scripts/build-cover.sh --text-only

word-count:
	@python3 ./scripts/word-count.py

clean:
	@./scripts/build-book.sh clean
