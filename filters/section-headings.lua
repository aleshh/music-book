-- Give reader-facing Section dividers separate label and title spans while
-- preserving the clean Markdown heading and its existing identifier.

function Header(header)
  if header.level ~= 1 then
    return nil
  end

  local text = pandoc.utils.stringify(header.content)
  local number, title = text:match("^Section%s+(%d+):%s+(.+)$")
  if not number then
    return nil
  end

  local parsed_title = pandoc.read(title, "markdown").blocks[1].content
  header.content = pandoc.Inlines({
    pandoc.Span(
      pandoc.Inlines({pandoc.Str("SECTION"), pandoc.Space(), pandoc.Str(number)}),
      pandoc.Attr("", {"section-label"})
    ),
    pandoc.SoftBreak(),
    pandoc.Span(parsed_title, pandoc.Attr("", {"section-name"})),
  })

  return header
end
