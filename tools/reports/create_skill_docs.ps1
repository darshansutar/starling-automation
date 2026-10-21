param([string]$OnlySkill = '')
$ErrorActionPreference = 'Stop'
$root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$records = Get-Content -LiteralPath "$root\tmp\pdfs\workflow-explanation\word-inputs.json" -Raw -Encoding UTF8 | ConvertFrom-Json
New-Item -ItemType Directory -Force -Path "$root\deliveries\workflow-explanation-2026-10-21\skill-documents" | Out-Null
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
$results = @()
try {
    foreach ($record in $records) {
        if ($OnlySkill -and $record.name -ne $OnlySkill) { continue }
        $doc = $word.Documents.Add()
        try {
            $doc.PageSetup.PaperSize = 7
            $doc.PageSetup.TopMargin = 43
            $doc.PageSetup.BottomMargin = 43
            $doc.PageSetup.LeftMargin = 46
            $doc.PageSetup.RightMargin = 46
            $normal = $doc.Styles.Item(-1)
            $normal.Font.Name = 'Arial'
            $normal.Font.Size = 10
            if ($record.name -in @('starling-cinematography', 'starling-animation-monitor')) { $normal.Font.Size = 9.5 }
            $normal.Font.Color = 0
            $normal.ParagraphFormat.SpaceAfter = 5
            if ($record.name -in @('starling-cinematography', 'starling-animation-monitor')) { $normal.ParagraphFormat.SpaceAfter = 4 }
            $normal.ParagraphFormat.LineSpacingRule = 0
            $intro = $record.title + "`r" + 'Complete current SKILL.md source' + "`r" + 'Snapshot 21 October 2026' + "`r" + 'Original file: ' + $record.source + "`r" + 'SHA256: ' + $record.sha256 + "`r" + 'The source text below is reproduced in full for manual review. Markdown syntax and reference paths are retained.' + "`r`r"
            $sourceText = $record.content.Replace("`r`n", "`n").Replace("`n", "`r")
            $appendix = if ($record.shared_contract) { "`r`r# Shared production contracts`r" + $record.shared_contract.Replace("`r`n", "`n").Replace("`n", "`r") } else { "" }
            $doc.Content.Text = $intro + $sourceText + $appendix
            $doc.Paragraphs.Item(1).Range.Style = $doc.Styles.Item(-63)
            $doc.Paragraphs.Item(1).Range.Font.Name = 'Arial'
            $doc.Paragraphs.Item(1).Range.Font.Size = 20
            $doc.Paragraphs.Item(1).Range.Font.Color = 0
            $doc.Paragraphs.Item(1).Range.Font.Underline = 0
            for ($n = 2; $n -le 6; $n++) { $doc.Paragraphs.Item($n).Range.Font.Size = 8 }
            foreach ($para in $doc.Paragraphs) {
                $line = $para.Range.Text.TrimEnd("`r")
                if ([string]::IsNullOrWhiteSpace($line)) {
                    $para.Range.Font.Size = 3
                    $para.Format.SpaceAfter = 0
                    $para.Format.SpaceBefore = 0
                    $para.Format.KeepWithNext = -1
                }
                if ($line.StartsWith('#')) {
                    $para.Range.Font.Bold = 1
                    $para.Range.Font.Size = 12
                    $para.Format.KeepWithNext = -1
                    $para.Format.SpaceBefore = 9
                }
            }
            $footer = $doc.Sections.Item(1).Footers.Item(1).Range
            $footer.Text = 'Skill source review  |  '
            $footer.Font.Name = 'Arial'
            $footer.Font.Size = 8
            $footer.Collapse(0)
            $null = $footer.Fields.Add($footer,33)
            $doc.SaveAs2([string]$record.output,16)
            $doc.ExportAsFixedFormat([string]$record.render,17)
            $results += [PSCustomObject]@{name=$record.name;docx=$record.output;pdf=$record.render;pages=$doc.ComputeStatistics(2)}
            Write-Output ('Created and rendered ' + $record.name)
        } finally { $doc.Close(0) }
    }
} finally { $word.Quit() }
$results | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath "$root\tmp\pdfs\workflow-explanation\word-render-results.json" -Encoding UTF8
