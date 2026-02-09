import React from 'react';
import { Routes, Route } from 'react-router-dom';
import KnowledgeListPage from './KnowledgeListPage';
import KnowledgeDetailPage from './KnowledgeDetailPage';
import KnowledgeEditorPage from './KnowledgeEditorPage';

const KnowledgePage: React.FC = () => {
  return (
    <Routes>
      <Route path="/" element={<KnowledgeListPage />} />
      <Route path="/new" element={<KnowledgeEditorPage />} />
      <Route path="/:id" element={<KnowledgeDetailPage />} />
      <Route path="/:id/edit" element={<KnowledgeEditorPage />} />
    </Routes>
  );
};

export default KnowledgePage;
