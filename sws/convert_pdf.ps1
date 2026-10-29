$docxPath = "C:\Users\Maryeel\Desktop\SystemPr\lab11\NguyenHoangLuc_Lab11_GroupProject.docx"
$pdfPath = "C:\Users\Maryeel\Desktop\SystemPr\lab11\NguyenHoangLuc_Lab11_GroupProject.pdf"

$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($docxPath)
    $doc.SaveAs([ref]$pdfPath, [ref]17)
    $doc.Close()
    Write-Host "Successfully converted $docxPath to $pdfPath"
} catch {
    Write-Error $_
} finally {
    $word.Quit()
}
