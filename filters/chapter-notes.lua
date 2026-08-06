-- Keep each chapter's notes with that chapter and restart numbering at 1.
-- This also prevents repeated Markdown labels such as [^1] from colliding
-- when Pandoc receives several chapter files at once.

local chapter_number = 0
local note_number = 0
local pending_notes = {}

local function anchor(identifier, class_name)
  return pandoc.Span({}, pandoc.Attr(identifier, {class_name}))
end

local function add_backlink(blocks, reference_id)
  local backlink = pandoc.Link({pandoc.Str("back")}, "#" .. reference_id)
  local last = blocks[#blocks]

  if last and (last.t == "Para" or last.t == "Plain") then
    last.content:insert(pandoc.Space())
    last.content:insert(backlink)
  else
    blocks:insert(pandoc.Plain({backlink}))
  end
end

local function prepare_note(note, note_id, reference_id)
  local blocks = note.content
  local first = blocks[1]
  local note_anchor = anchor(note_id, "note-anchor")

  if first and (first.t == "Para" or first.t == "Plain") then
    first.content:insert(1, pandoc.Space())
    first.content:insert(1, note_anchor)
  else
    blocks:insert(1, pandoc.Plain({note_anchor}))
  end

  add_backlink(blocks, reference_id)
  return blocks
end

local function replace_note(note)
  note_number = note_number + 1

  local suffix = tostring(chapter_number) .. "-" .. tostring(note_number)
  local note_id = "chapter-note-" .. suffix
  local reference_id = "chapter-note-ref-" .. suffix

  pending_notes[#pending_notes + 1] = prepare_note(note, note_id, reference_id)

  local number = pandoc.Str(tostring(note_number))
  local link = pandoc.Link({number}, "#" .. note_id)
  local marker = pandoc.Superscript({link})
  return pandoc.Span({marker}, pandoc.Attr(reference_id, {"note-ref"}))
end

local function notes_div(header)
  local items = pending_notes
  pending_notes = {}
  return pandoc.Div(
    {header, pandoc.OrderedList(items)},
    pandoc.Attr("", {"chapter-notes"})
  )
end

local function is_notes_header(block)
  return block.t == "Header"
    and block.level == 2
    and pandoc.utils.stringify(block.content):lower() == "notes"
end

function Pandoc(document)
  local result = pandoc.Blocks({})

  for _, block in ipairs(document.blocks) do
    if block.t == "Header" and block.level == 1 then
      if #pending_notes > 0 then
        result:insert(notes_div(pandoc.Header(2, {pandoc.Str("Notes")})))
      end
      chapter_number = chapter_number + 1
      note_number = 0
    end

    if is_notes_header(block) then
      result:insert(notes_div(block))
    else
      result:insert(pandoc.walk_block(block, {Note = replace_note}))
    end
  end

  if #pending_notes > 0 then
    result:insert(notes_div(pandoc.Header(2, {pandoc.Str("Notes")})))
  end

  document.blocks = result
  return document
end
